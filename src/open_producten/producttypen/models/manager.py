# from django.db.models import CharField, Manager, OuterRef, Subquery, TextField
#
# from open_producten.producttypen.models import ProductTypeVertaling
#
#
# class ProductTypeTranslationManager(Manager):
#
#     def language(self, language_code):
#         vertaling = ProductTypeVertaling.objects.filter(
#             product_type=OuterRef("pk"), taalcode="en"
#         )
#
#         naam = vertaling.values("naam")
#         samenvatting = vertaling.values("samenvatting")
#
#         return self.annotate(
#             en_naam=Subquery(naam, output_field=CharField()),
#             en_samenvatting=Subquery(samenvatting, output_field=TextField()),
#         )
