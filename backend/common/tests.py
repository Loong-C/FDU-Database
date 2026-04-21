from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITransactionTestCase

from catalog.models import Product
from common.testing import bootstrap_business_schema

User = get_user_model()


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class BookstoreAPITests(APITransactionTestCase):
    reset_sequences = True

    def setUp(self):
        super().setUp()
        bootstrap_business_schema(include_seed=True, include_views=True)
        self._seed_users()

    def _seed_users(self):
        demo_users = [
            ("admin", "Admin123!", "admin"),
            ("operator", "Operator123!", "operator"),
            ("viewer", "Viewer123!", "viewer"),
        ]
        for username, password, role in demo_users:
            user = User.objects.create_user(
                username=username,
                password=password,
                role=role,
                display_name=username.title(),
                is_active=True,
            )
            user.save()

    def login_client(self, username, password):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["data"]["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client, response.data["data"]

    def test_auth_login_refresh_logout_flow(self):
        client, tokens = self.login_client("admin", "Admin123!")
        me_response = client.get("/api/v1/auth/me")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["data"]["username"], "admin")

        refresh_response = APIClient().post(
            "/api/v1/auth/refresh",
            {"refresh_token": tokens["refresh_token"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_refresh_token = refresh_response.data["data"]["refresh_token"]

        logout_response = client.post(
            "/api/v1/auth/logout",
            {"refresh_token": new_refresh_token},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        failed_refresh = APIClient().post(
            "/api/v1/auth/refresh",
            {"refresh_token": new_refresh_token},
            format="json",
        )
        self.assertEqual(failed_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_permissions_matrix(self):
        viewer_client, _ = self.login_client("viewer", "Viewer123!")
        analytics_response = viewer_client.get("/api/v1/analytics/stores/daily")
        self.assertEqual(analytics_response.status_code, status.HTTP_200_OK)
        stores_forbidden = viewer_client.get("/api/v1/stores")
        self.assertEqual(stores_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        operator_client, _ = self.login_client("operator", "Operator123!")
        stores_ok = operator_client.get("/api/v1/stores")
        self.assertEqual(stores_ok.status_code, status.HTTP_200_OK)
        create_customer = operator_client.post(
            "/api/v1/customers",
            {
                "customer_name": "新客户",
                "phone": "13800000088",
                "email": "new_customer@example.com",
                "address": "上海市徐汇区1号",
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(create_customer.status_code, status.HTTP_201_CREATED)
        create_store_forbidden = operator_client.post(
            "/api/v1/stores",
            {
                "store_name": "广州天河店",
                "city": "广州",
                "address": "天河区体育西路1号",
                "phone": "020-88880003",
                "manager_name": "李华",
            },
            format="json",
        )
        self.assertEqual(create_store_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        admin_client, _ = self.login_client("admin", "Admin123!")
        create_store = admin_client.post(
            "/api/v1/stores",
            {
                "store_name": "广州天河店",
                "city": "广州",
                "address": "天河区体育西路1号",
                "phone": "020-88880003",
                "manager_name": "李华",
            },
            format="json",
        )
        self.assertEqual(create_store.status_code, status.HTTP_201_CREATED)
        users_response = admin_client.get("/api/v1/users")
        self.assertEqual(users_response.status_code, status.HTTP_200_OK)

    def test_catalog_customer_and_member_crud(self):
        admin_client, _ = self.login_client("admin", "Admin123!")

        product_response = admin_client.post(
            "/api/v1/products",
            {
                "product_name": "金属书签",
                "category_id": 4,
                "unit": "个",
                "unit_price": "9.90",
                "cost_price": "4.20",
                "stock_qty": 120,
                "barcode": "690123450099",
                "status": "onsale",
                "supplier_links": [
                    {
                        "supplier_id": 1,
                        "supply_price": "3.80",
                        "min_order_qty": 10,
                        "is_primary": True,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(product_response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(product_response.data["data"]["is_book"])

        book_response = admin_client.post(
            "/api/v1/books",
            {
                "product_name": "Python Web 开发实战",
                "category_id": 3,
                "unit": "本",
                "unit_price": "98.00",
                "cost_price": "66.00",
                "stock_qty": 40,
                "barcode": "9787111000999",
                "status": "onsale",
                "supplier_links": [
                    {
                        "supplier_id": 2,
                        "supply_price": "60.00",
                        "min_order_qty": 5,
                        "is_primary": True,
                    }
                ],
                "isbn": "9787111000999",
                "publisher_id": 1,
                "publish_date": "2024-03-01",
                "edition": "第1版",
                "language": "中文",
                "page_count": 388,
                "author_ids": [1],
                "translator_ids": [],
            },
            format="json",
        )
        self.assertEqual(book_response.status_code, status.HTTP_201_CREATED)
        book_id = book_response.data["data"]["product_id"]

        book_patch = admin_client.patch(
            f"/api/v1/books/{book_id}",
            {
                "stock_qty": 55,
                "status": "offsale",
                "author_ids": [1, 3],
            },
            format="json",
        )
        self.assertEqual(book_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(len(book_patch.data["data"]["authors"]), 2)

        operator_client, _ = self.login_client("operator", "Operator123!")
        customer_response = operator_client.post(
            "/api/v1/customers",
            {
                "customer_name": "王小明",
                "phone": "13800000077",
                "email": "wangxiaoming@example.com",
                "address": "北京市海淀区中关村1号",
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(customer_response.status_code, status.HTTP_201_CREATED)
        customer_id = customer_response.data["data"]["customer_id"]

        member_response = operator_client.post(
            "/api/v1/members",
            {
                "customer_id": customer_id,
                "member_no": "M20259999",
                "level": "silver",
                "points": 80,
                "join_date": "2026-04-01",
            },
            format="json",
        )
        self.assertEqual(member_response.status_code, status.HTTP_201_CREATED)
        patch_member = operator_client.patch(
            f"/api/v1/members/{customer_id}",
            {"points": 120, "level": "gold"},
            format="json",
        )
        self.assertEqual(patch_member.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_member.data["data"]["points"], 120)

    def test_sale_inventory_lifecycle(self):
        operator_client, _ = self.login_client("operator", "Operator123!")
        product4_before = Product.objects.get(pk=4).stock_qty
        product5_before = Product.objects.get(pk=5).stock_qty

        create_sale_response = operator_client.post(
            "/api/v1/sales",
            {
                "store_id": 1,
                "customer_id": 1,
                "sale_time": timezone.now().isoformat(),
                "payment_method": "wechat",
                "discount_amount": "5.00",
                "items": [
                    {"product_id": 4, "quantity": 20},
                    {"product_id": 5, "quantity": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(create_sale_response.status_code, status.HTTP_201_CREATED)
        sale_id = create_sale_response.data["data"]["sale_id"]
        self.assertEqual(Decimal(create_sale_response.data["data"]["total_amount"]), Decimal("82.00"))
        self.assertEqual(Decimal(create_sale_response.data["data"]["actual_amount"]), Decimal("77.00"))
        self.assertEqual(Product.objects.get(pk=4).stock_qty, product4_before - 20)
        self.assertEqual(Product.objects.get(pk=5).stock_qty, product5_before - 1)

        update_sale_response = operator_client.patch(
            f"/api/v1/sales/{sale_id}",
            {
                "discount_amount": "2.00",
                "items": [
                    {"product_id": 4, "quantity": 10},
                ],
            },
            format="json",
        )
        self.assertEqual(update_sale_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=4).stock_qty, product4_before - 10)
        self.assertEqual(Product.objects.get(pk=5).stock_qty, product5_before)

        delete_response = operator_client.delete(f"/api/v1/sales/{sale_id}")
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=4).stock_qty, product4_before)
        self.assertEqual(Product.objects.get(pk=5).stock_qty, product5_before)

    def test_validation_conflict_and_analytics(self):
        admin_client, _ = self.login_client("admin", "Admin123!")
        operator_client, _ = self.login_client("operator", "Operator123!")
        viewer_client, _ = self.login_client("viewer", "Viewer123!")

        future_book = admin_client.post(
            "/api/v1/books",
            {
                "product_name": "未来出版图书",
                "category_id": 3,
                "unit": "本",
                "unit_price": "88.00",
                "cost_price": "55.00",
                "stock_qty": 10,
                "barcode": "9787111000666",
                "status": "onsale",
                "isbn": "9787111000666",
                "publisher_id": 1,
                "publish_date": (date.today() + timedelta(days=1)).isoformat(),
                "author_ids": [1],
            },
            format="json",
        )
        self.assertEqual(future_book.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        missing_member = operator_client.post(
            "/api/v1/members",
            {
                "customer_id": 9999,
                "member_no": "M99999999",
                "level": "silver",
                "points": 10,
                "join_date": "2026-04-01",
            },
            format="json",
        )
        self.assertEqual(missing_member.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        delete_supplier = admin_client.delete("/api/v1/suppliers/1")
        self.assertEqual(delete_supplier.status_code, status.HTTP_409_CONFLICT)

        delete_product = admin_client.delete("/api/v1/products/1")
        self.assertEqual(delete_product.status_code, status.HTTP_409_CONFLICT)

        store_daily = viewer_client.get(
            "/api/v1/analytics/stores/daily",
            {"store_id": 1, "date_from": "2026-04-10", "date_to": "2026-04-10"},
        )
        self.assertEqual(store_daily.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(store_daily.data["data"]), 1)

        product_rank = viewer_client.get(
            "/api/v1/analytics/products/rank",
            {"category_id": 3, "date_from": "2026-04-10", "date_to": "2026-04-11", "limit": 5},
        )
        self.assertEqual(product_rank.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(product_rank.data["data"]), 1)

        member_rank = viewer_client.get(
            "/api/v1/analytics/members/rank",
            {"level": "gold", "date_from": "2026-04-10", "date_to": "2026-04-11", "limit": 5},
        )
        self.assertEqual(member_rank.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(member_rank.data["data"]), 1)

        category_summary = viewer_client.get(
            "/api/v1/analytics/categories/summary",
            {"date_from": "2026-04-10", "date_to": "2026-04-11"},
        )
        self.assertEqual(category_summary.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(category_summary.data["data"]), 1)
