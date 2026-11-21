from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdministradorViewSet,
    AuditoriaViewSet,
    ConsultaViewSet,
    DetalleRecetaViewSet,
    EspecialidadViewSet,
    EstudioImagenViewSet,
    HealthView,
    LoginView,
    LogoutView,
    MedicamentoViewSet,
    MedicoViewSet,
    MenuViewSet,
    PacienteViewSet,
    PerfilView,
    PersonalClinicaViewSet,
    RecetaElectronicaViewSet,
    ResultadoLaboratorioViewSet,
    SedeViewSet,
    SincronizarImagenesView,
    SincronizarLaboratorioView,
    WebhookImagenesView,
    WebhookLaboratorioView,
)

router = DefaultRouter()
router.register('pacientes', PacienteViewSet, basename='paciente')
router.register('consultas', ConsultaViewSet, basename='consulta')
router.register('recetas', RecetaElectronicaViewSet, basename='receta')
router.register('detalles-receta', DetalleRecetaViewSet, basename='detalle-receta')
router.register('medicamentos', MedicamentoViewSet, basename='medicamento')
router.register('resultados-laboratorio', ResultadoLaboratorioViewSet, basename='resultado-laboratorio')
router.register('estudios-imagen', EstudioImagenViewSet, basename='estudio-imagen')
router.register('auditorias', AuditoriaViewSet, basename='auditoria')
router.register('medicos', MedicoViewSet, basename='medico')
router.register('especialidades', EspecialidadViewSet, basename='especialidad')
router.register('sedes', SedeViewSet, basename='sede')
router.register('personal-clinica', PersonalClinicaViewSet, basename='personal-clinica')
router.register('administradores', AdministradorViewSet, basename='administrador')
router.register('menu', MenuViewSet, basename='menu')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('health/', HealthView.as_view(), name='health'),
    path(
        'resultados-laboratorio/sincronizar/',
        SincronizarLaboratorioView.as_view(),
        name='sincronizar-laboratorio',
    ),
    path('estudios-imagen/sincronizar/', SincronizarImagenesView.as_view(), name='sincronizar-imagenes'),
    path('webhooks/laboratorio/', WebhookLaboratorioView.as_view(), name='webhook-laboratorio'),
    path('webhooks/imagenes/', WebhookImagenesView.as_view(), name='webhook-imagenes'),
    path('', include(router.urls)),
]
