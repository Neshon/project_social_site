from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500


handler404 = 'posts.views.page_not_found' # noqa
handler500 = 'posts.views.server_error' # noqa


urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]


urlpatterns += [
        path('about-spec/', views.flatpage, {'url': 'about-spec/'}, name='about'),
        path('about-author/',
             views.flatpage,
             {'url': 'about-author/'},
             name='terms'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
