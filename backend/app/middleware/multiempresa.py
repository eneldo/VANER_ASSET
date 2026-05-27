from fastapi import Request

class MultiEmpresaMiddleware:
    async def __call__(self, request: Request, call_next):
        empresa_id = request.headers.get("X-Empresa-ID")
        request.state.empresa_id = empresa_id
        response = await call_next(request)
        return response
