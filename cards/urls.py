from django.urls import path

from . import views

app_name = "cards"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.home, name="dashboard"),
    path("cards/", views.browse_cards, name="browse"),
    path("cards/create/", views.create_card, name="create"),
    path("cards/<int:card_id>/edit/", views.edit_card, name="edit"),
    path("cards/<int:card_id>/delete/", views.delete_card, name="delete"),
    path("cards/<int:card_id>/images/add/", views.add_images, name="add_images"),
    path("cards/search-image/", views.image_search, name="search_image"),
    path("cards/<int:card_id>/", views.card_detail, name="detail"),
]
