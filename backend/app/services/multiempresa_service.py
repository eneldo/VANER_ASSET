class MultiEmpresaService:

    @staticmethod
    def filtrar_empresa(query, empresa_id):
        return query.filter_by(empresa_id=empresa_id)
