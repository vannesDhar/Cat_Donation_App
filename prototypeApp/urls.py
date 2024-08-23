from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage, name="homepage"),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('adoption/', views.adoption, name='adoption'),
    path('adopt/', views.handle_adoption, name='handle_adoption'),
    path('community_cats/',views.community_cat, name='community_cats'),
    path('api/community-cats/', views.community_cat_list, name='list_community_cats'),
    path('api/community-cats/search/', views.search_community_cat, name='search_community_cats'),
    path('api/community-cats/submit/', views.submit_community_cat, name='submit_community_cat'),
    path('logout/', views.logout_account, name="logout"),
    path('profile', views.profile, name='profile'),
    path('api/profile/', views.profile_detail, name='api_profile'),
    path('api/cats/', views.cat_list, name='cat_list'),
    
    path('api/threads/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('api/threads/create/', views.create_thread, name='api_create_thread'),
    path('api/threads/list', views.thread_list, name='thread_list'),
    path('thread/', views.render_thread, name='thread'),
    path('thread/render_create_thread/',views.render_create_thread, name='render_create_thread'),
    path('render_thread_details/<int:thread_id>/',views.render_thread_details, name='render_thread_details'),
    path('api/create_comment/<int:thread_id>/', views.create_comment, name='create_comment'),
    path('api/thread/<int:thread_id>/comments/', views.get_comments, name='get_comments'),


    path('donation/', views.donation, name="donation"),
    path('config/', views.stripe_config),
    path('donation/create-checkout-session/', views.create_checkout_session,name='create_checkout_session'),
    path('success/', views.successView, name="success"),
]