from django.test import TestCase

from ..admin.category import CategoryAdminForm
from .factories import CategoryFactory


def create_form(data, instance=None):
    return CategoryAdminForm(
        instance=instance,
        data=data,
    )


class TestCategoryAdminForm(TestCase):

    def setUp(self):
        self.data = {
            "name": "test",
            "_position": "first-child",
            "slug": "test",
            "path": "0005",
            "numchild": 1,
            "depth": 1,
        }

    def test_parent_nodes_must_be_published(self):
        parent = CategoryFactory.create(published=False)
        data = self.data | {"published": True, "_ref_node_id": parent.id}

        form = create_form(data)

        self.assertEquals(
            form.errors,
            {
                "__all__": [
                    "Parent nodes have to be published in order to publish a child."
                ]
            },
        )

        parent.published = True
        parent.save()

        form = create_form(data)
        self.assertEquals(form.errors, {})

    def test_parent_nodes_cannot_be_unpublished_with_published_children(self):
        parent = CategoryFactory.create(published=False)
        parent.add_child(**{"name": "child", "slug": "child", "published": True})
        data = self.data | {"published": False, "_ref_node_id": None}

        form = create_form(data, parent)

        self.assertEquals(
            form.errors,
            {
                "__all__": [
                    "Parent nodes cannot be unpublished if they have published children."
                ]
            },
        )
