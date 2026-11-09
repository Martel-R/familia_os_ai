import logging
from typing import Dict, Any
from sqlalchemy import create_engine, text
from app.config import settings

logger = logging.getLogger(__name__)

MULTITENANT_MIGRATION_SQL = """
CREATE SCHEMA IF NOT EXISTS familialm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS familialm.familias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    slug VARCHAR(100),
    codigo_convite VARCHAR(30) UNIQUE DEFAULT UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8)),
    plano VARCHAR(50) DEFAULT 'familiar',
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

INSERT INTO familialm.familias (id, nome, slug, codigo_convite, plano, ativo)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Família Martel',
    'familia-martel',
    'MARTEL',
    'premium',
    TRUE
)
ON CONFLICT (id) DO NOTHING;

DO $$
DECLARE
    tbl TEXT;
    tabelas TEXT[] := ARRAY[
        'usuarios', 'contas_bancarias', 'categorias_financeiras', 'cofrinhos',
        'cofrinhos_aportes', 'despesas_recorrentes', 'transacoes_financeiras',
        'integracoes_google', 'eventos', 'convidados', 'eventos_tarefas',
        'cotacoes', 'cofre_credenciais', 'tarefas_rotinas', 'loja_privilegios',
        'resgates_privilegios', 'agenda_contatos', 'inventario_itens',
        'historico_manutencoes', 'saude_checkins', 'saude_fichas_medicas',
        'saude_medicamentos', 'saude_vacinacao', 'saude_consultas_exames',
        'saude_metricas_vitais', 'compras_recibos', 'compras_itens_extraidos',
        'mural_conquistas', 'mural_fotos', 'configuracoes_casa'
    ];
BEGIN
    FOREACH tbl IN ARRAY tabelas LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'familialm' AND table_name = tbl
        ) THEN
            EXECUTE format(
                'ALTER TABLE familialm.%I ADD COLUMN IF NOT EXISTS familia_id UUID REFERENCES familialm.familias(id) ON DELETE CASCADE;',
                tbl
            );
            EXECUTE format(
                'CREATE INDEX IF NOT EXISTS idx_%s_familia_id ON familialm.%I(familia_id);',
                tbl, tbl
            );
        END IF;
    END LOOP;
END $$;

ALTER TABLE familialm.categorias_financeiras DROP CONSTRAINT IF EXISTS categorias_financeiras_nome_key;
ALTER TABLE familialm.agenda_contatos DROP CONSTRAINT IF EXISTS agenda_contatos_telefone_key;
ALTER TABLE familialm.configuracoes_casa ALTER COLUMN id TYPE VARCHAR(150);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'categorias_financeiras_familia_nome_key'
    ) THEN
        ALTER TABLE familialm.categorias_financeiras
            ADD CONSTRAINT categorias_financeiras_familia_nome_key UNIQUE (familia_id, nome);
    END IF;
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

UPDATE familialm.usuarios
SET familia_id = '00000000-0000-0000-0000-000000000001'
WHERE familia_id IS NULL AND ativo = TRUE;

DO $$
DECLARE
    tbl TEXT;
    tabelas_dados TEXT[] := ARRAY[
        'contas_bancarias', 'cofrinhos', 'cofrinhos_aportes', 'despesas_recorrentes',
        'transacoes_financeiras', 'integracoes_google', 'eventos', 'convidados',
        'eventos_tarefas', 'cotacoes', 'cofre_credenciais', 'tarefas_rotinas',
        'loja_privilegios', 'resgates_privilegios', 'agenda_contatos',
        'inventario_itens', 'historico_manutencoes', 'saude_checkins',
        'saude_fichas_medicas', 'saude_medicamentos', 'saude_vacinacao',
        'saude_consultas_exames', 'saude_metricas_vitais', 'compras_recibos',
        'compras_itens_extraidos', 'mural_conquistas', 'mural_fotos',
        'configuracoes_casa'
    ];
BEGIN
    FOREACH tbl IN ARRAY tabelas_dados LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'familialm' AND table_name = tbl
        ) THEN
            EXECUTE format(
                'UPDATE familialm.%I SET familia_id = ''00000000-0000-0000-0000-000000000001'' WHERE familia_id IS NULL;',
                tbl
            );
        END IF;
    END LOOP;
END $$;

CREATE OR REPLACE FUNCTION familialm.get_user_familia_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = familialm, public
AS $$
    SELECT familia_id
    FROM familialm.usuarios
    WHERE auth_user_id = auth.uid()
      AND ativo = TRUE
      AND familia_id IS NOT NULL
    ORDER BY criado_em ASC
    LIMIT 1;
$$;

GRANT EXECUTE ON FUNCTION familialm.get_user_familia_id() TO anon, authenticated, service_role;

CREATE OR REPLACE FUNCTION familialm.preencher_familia_id_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = familialm, public
AS $$
DECLARE
    v_familia_id UUID;
BEGIN
    IF NEW.familia_id IS NULL THEN
        v_familia_id := familialm.get_user_familia_id();
        IF v_familia_id IS NOT NULL THEN
            NEW.familia_id := v_familia_id;
        ELSE
            NEW.familia_id := '00000000-0000-0000-0000-000000000001'::UUID;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DO $$
DECLARE
    tbl TEXT;
    tabelas_trigger TEXT[] := ARRAY[
        'contas_bancarias', 'cofrinhos', 'cofrinhos_aportes', 'despesas_recorrentes',
        'transacoes_financeiras', 'integracoes_google', 'eventos', 'convidados',
        'eventos_tarefas', 'cotacoes', 'cofre_credenciais', 'tarefas_rotinas',
        'loja_privilegios', 'resgates_privilegios', 'agenda_contatos',
        'inventario_itens', 'historico_manutencoes', 'saude_checkins',
        'saude_fichas_medicas', 'saude_medicamentos', 'saude_vacinacao',
        'saude_consultas_exames', 'saude_metricas_vitais', 'compras_recibos',
        'compras_itens_extraidos', 'mural_conquistas', 'mural_fotos',
        'configuracoes_casa'
    ];
BEGIN
    FOREACH tbl IN ARRAY tabelas_trigger LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'familialm' AND table_name = tbl
        ) THEN
            EXECUTE format(
                'ALTER TABLE familialm.%I ALTER COLUMN familia_id SET DEFAULT familialm.get_user_familia_id();',
                tbl
            );
            EXECUTE format(
                'DROP TRIGGER IF EXISTS trg_set_familia_id ON familialm.%I;',
                tbl
            );
            EXECUTE format(
                'CREATE TRIGGER trg_set_familia_id BEFORE INSERT ON familialm.%I FOR EACH ROW EXECUTE FUNCTION familialm.preencher_familia_id_trigger();',
                tbl
            );
        END IF;
    END LOOP;
END $$;

ALTER TABLE familialm.familias ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Acesso familias multi-tenant" ON familialm.familias;
CREATE POLICY "Acesso familias multi-tenant" ON familialm.familias
    FOR ALL
    TO anon, authenticated, service_role
    USING (
        auth.role() = 'service_role'
        OR auth.uid() IS NULL
        OR id = familialm.get_user_familia_id()
        OR familialm.get_user_familia_id() IS NULL
    )
    WITH CHECK (true);

DO $$
DECLARE
    tbl TEXT;
    tabelas_rls TEXT[] := ARRAY[
        'usuarios', 'contas_bancarias', 'categorias_financeiras', 'cofrinhos',
        'cofrinhos_aportes', 'despesas_recorrentes', 'transacoes_financeiras',
        'integracoes_google', 'eventos', 'convidados', 'eventos_tarefas',
        'cotacoes', 'cofre_credenciais', 'tarefas_rotinas', 'loja_privilegios',
        'resgates_privilegios', 'agenda_contatos', 'inventario_itens',
        'historico_manutencoes', 'saude_checkins', 'saude_fichas_medicas',
        'saude_medicamentos', 'saude_vacinacao', 'saude_consultas_exames',
        'saude_metricas_vitais', 'compras_recibos', 'compras_itens_extraidos',
        'mural_conquistas', 'mural_fotos', 'configuracoes_casa'
    ];
BEGIN
    FOREACH tbl IN ARRAY tabelas_rls LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'familialm' AND table_name = tbl
        ) THEN
            EXECUTE format('ALTER TABLE familialm.%I ENABLE ROW LEVEL SECURITY;', tbl);
            EXECUTE format('DROP POLICY IF EXISTS "Isolamento multi-tenant familia" ON familialm.%I;', tbl);
            EXECUTE format(
                'CREATE POLICY "Isolamento multi-tenant familia" ON familialm.%I
                 FOR ALL
                 TO anon, authenticated, service_role
                 USING (
                     auth.role() = ''service_role''
                     OR familia_id IS NULL
                     OR familia_id = COALESCE(familialm.get_user_familia_id(), ''00000000-0000-0000-0000-000000000001''::UUID)
                 )
                 WITH CHECK (
                     auth.role() = ''service_role''
                     OR familia_id IS NULL
                     OR familia_id = COALESCE(familialm.get_user_familia_id(), ''00000000-0000-0000-0000-000000000001''::UUID)
                 );',
                tbl
            );
        END IF;
    END LOOP;
END $$;

GRANT USAGE ON SCHEMA familialm TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA familialm TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA familialm TO anon, authenticated, service_role;

ALTER TABLE familialm.compras_itens_extraidos
    ADD COLUMN IF NOT EXISTS codigo_produto VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_compras_itens_codigo_produto
    ON familialm.compras_itens_extraidos(familia_id, codigo_produto);

CREATE TABLE IF NOT EXISTS familialm.compras_catalogo_produtos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    familia_id UUID NOT NULL DEFAULT familialm.get_user_familia_id() REFERENCES familialm.familias(id) ON DELETE CASCADE,
    fornecedor VARCHAR(255) NOT NULL,
    fornecedor_normalizado VARCHAR(255) NOT NULL,
    codigo_produto VARCHAR(100) NOT NULL,
    nome_produto VARCHAR(255) NOT NULL,
    categoria_sugerida VARCHAR(100) DEFAULT 'Alimentação',
    ultimo_valor_unitario NUMERIC(12,2) DEFAULT 0,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT compras_catalogo_chave_composta_uk UNIQUE (familia_id, fornecedor_normalizado, codigo_produto)
);

CREATE INDEX IF NOT EXISTS idx_compras_catalogo_chave
    ON familialm.compras_catalogo_produtos(familia_id, fornecedor_normalizado, codigo_produto);

DROP TRIGGER IF EXISTS trg_set_familia_id ON familialm.compras_catalogo_produtos;
CREATE TRIGGER trg_set_familia_id
    BEFORE INSERT ON familialm.compras_catalogo_produtos
    FOR EACH ROW EXECUTE FUNCTION familialm.preencher_familia_id_trigger();

ALTER TABLE familialm.compras_catalogo_produtos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Isolamento multi-tenant familia" ON familialm.compras_catalogo_produtos;
CREATE POLICY "Isolamento multi-tenant familia" ON familialm.compras_catalogo_produtos
    FOR ALL
    TO anon, authenticated, service_role
    USING (
        auth.role() = 'service_role'
        OR familia_id IS NULL
        OR familia_id = COALESCE(familialm.get_user_familia_id(), '00000000-0000-0000-0000-000000000001'::UUID)
    )
    WITH CHECK (
        auth.role() = 'service_role'
        OR familia_id IS NULL
        OR familia_id = COALESCE(familialm.get_user_familia_id(), '00000000-0000-0000-0000-000000000001'::UUID)
    );

GRANT ALL ON TABLE familialm.compras_catalogo_produtos TO anon, authenticated, service_role;
NOTIFY pgrst, 'reload schema';
"""


def run_multitenant_migrations() -> Dict[str, Any]:
    if not settings.SUPABASE_DB_URL:
        return {
            "executado": False,
            "motivo": "SUPABASE_DB_URL não configurado no ambiente.",
        }

    try:
        engine = create_engine(settings.SUPABASE_DB_URL)
        with engine.begin() as conn:
            conn.execute(text(MULTITENANT_MIGRATION_SQL))
        logger.info("Migração multi-tenant aplicada com sucesso no schema familialm.")
        return {
            "executado": True,
            "mensagem": "Migração multi-tenant aplicada com sucesso no schema familialm.",
        }
    except Exception as e:
        logger.error(f"Erro ao executar migração multi-tenant: {e}")
        return {
            "executado": False,
            "erro": str(e),
        }
