from django.test import TestCase

from ..admin.category import CategoryAdminForm
from ..models import Category
from .factories import CategoryFactory


class TestCategoryAdminForm(TestCase):

    def setUp(self):
        self.parent: Category = CategoryFactory.create(published=False)
        self.data = {
            "name": "test",
            "published": True,
            "_ref_node_id": self.parent.id,
            "_position": "first-child",
            "slug": "test",
            "path": "0005",
            "numchild": 1,
            "depth": 1,
        }

    def test_parent_nodes_must_be_published(self):
        form = CategoryAdminForm(data=self.data)

        self.assertEquals(
            form.errors,
            {
                "__all__": [
                    "Parent nodes have to be published in order to publish a child."
                ]
            },
        )

        self.parent.published = True
        self.parent.save()

        form = CategoryAdminForm(data=self.data)
        self.assertEquals(form.errors, {})

    def test_parent_nodes_cannot_be_unpublished_with_published_children(self):
        def create_form(instance):
            return CategoryAdminForm(
                instance=instance,
                data=self.data | {"published": False, "_ref_node_id": None},
            )

        def get_category():
            return Category.objects.get(pk=self.parent.id)

        form = create_form(self.parent)

        self.assertEquals(form.errors, {})

        child = get_category().add_child(
            **{"name": "child", "slug": "child", "published": False}
        )
        parent = get_category()
        form = create_form(parent)

        self.assertEquals(form.errors, {})

        child.published = True
        child.save()

        parent = get_category()
        form = create_form(parent)

        self.assertEquals(
            form.errors,
            {
                "__all__": [
                    "Parent nodes cannot be unpublished if they have published children."
                ]
            },
        )


# TODO
class TestCategoryAdminFormSet(TestCase):
    def setUp(self):
        pass

    def test_parent_nodes_cannot_be_unpublished_with_published_children(self):
        pass

    def test_parent_nodes_must_be_published_to_publish_children(self):
        pass
