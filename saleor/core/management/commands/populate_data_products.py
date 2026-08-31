import os
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify

from saleor.product.models import (
    Category,
    ProductType,
    Product,
    ProductVariant,
    ProductChannelListing,
    ProductVariantChannelListing,
    ProductMedia,
)
from saleor.attribute.models import (
    Attribute,
    AttributeValue,
    AttributeProduct,
    AssignedProductAttributeValue,
)
from saleor.channel.models import Channel
from saleor.warehouse.models import Warehouse, Stock


class Command(BaseCommand):
    help = "Populate InsaiVue High-Tech Data Products into Saleor DB"

    def handle(self, *args, **options):
        self.stdout.write("Starting InsaiVue Data Products Population...")

        # 1. Get default channels & warehouse
        channel_usd = Channel.objects.filter(slug="default-channel").first() or Channel.objects.first()
        channel_pln = Channel.objects.filter(slug="channel-pln").first()
        warehouse = Warehouse.objects.first()

        if not channel_usd:
            self.stderr.write("No active channel found! Aborting.")
            return

        # 2. Category
        category, _ = Category.objects.get_or_create(
            slug="data-products",
            defaults={
                "name": "數據產品 (Data Products)",
                "description": {
                    "time": 1725140000000,
                    "blocks": [
                        {
                            "data": {"text": "經過 AI 治理與隱私合規清洗之高品質零售與商圈人流數據資產。"},
                            "type": "paragraph"
                        }
                    ],
                    "version": "2.28.0"
                },
                "description_plaintext": "經過 AI 治理與隱私合規清洗之高品質零售與商圈人流數據資產。"
            }
        )
        self.stdout.write(f"Category: {category.name}")

        # 3. Product Type
        product_type, _ = ProductType.objects.get_or_create(
            slug="data-asset",
            defaults={
                "name": "Data Asset (數據資產)",
                "has_variants": False,
                "is_shipping_required": False,
                "is_digital": True
            }
        )
        self.stdout.write(f"ProductType: {product_type.name}")

        # 4. Attributes
        attrs_def = [
            ("Data Coverage", "data-coverage", ["台北信義商圈 A9 館 1F 門市全域", "信義計畫區核心步行商圈", "全台重點百貨連鎖"]),
            ("Data Period", "data-period", ["2024-Q1 ~ 2026-Q2", "2024-2026 歷年檔期", "近 3 年即時滾動"]),
            ("Sample Size", "sample-size", ["1,280,000+ 筆", "3,500,000+ 筆", "850,000+ 筆"]),
            ("Compliance Grade", "compliance-grade", ["Tier-A / GDPR-ready / ISO-27001", "Tier-A (去識別化驗證)"]),
            ("Update Frequency", "update-frequency", ["每週滾動更新 (Weekly Rolling)", "每日即時更新", "每月彙總"]),
            ("Data Format", "data-format", ["API / Parquet / Snowflake Data Share", "REST API & JSON Stream"]),
            ("License Type", "license-type", ["內部商業使用授權 (Internal Commercial Use)"])
        ]

        attr_objs = {}
        for name, slug, vals in attrs_def:
            attr, _ = Attribute.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "type": "product-type",
                    "input_type": "dropdown"
                }
            )
            AttributeProduct.objects.get_or_create(attribute=attr, product_type=product_type)
            attr_objs[slug] = attr
            
            for v in vals:
                AttributeValue.objects.get_or_create(
                    attribute=attr,
                    slug=slugify(v) or v.lower()[:50],
                    defaults={"name": v}
                )

        # 5. Products Definition
        products_data = [
            {
                "name": "新光三越 A9 一樓消費者輪廓分析",
                "slug": "skm-a9-1f-consumer-profile",
                "price_usd": Decimal("100.00"),
                "price_pln": Decimal("400.00"),
                "rating": 4.8,
                "images": ["demographics.png", "neural_network.png"],
                "summary": "深入解析 A9 1F 美妝與精品專櫃客群輪廓，25-34 歲女性佔比達 38%，週末停留時長與高客單價動線熱點分析。",
                "attributes": {
                    "data-coverage": "台北信義商圈 A9 館 1F 門市全域",
                    "data-period": "2024-Q1 ~ 2026-Q2",
                    "sample-size": "1,280,000+ 筆",
                    "compliance-grade": "Tier-A / GDPR-ready / ISO-27001",
                    "update-frequency": "每週滾動更新 (Weekly Rolling)",
                    "data-format": "API / Parquet / Snowflake Data Share",
                    "license-type": "內部商業使用授權 (Internal Commercial Use)"
                }
            },
            {
                "name": "信義商圈人流趨勢",
                "slug": "xinyi-district-foot-traffic",
                "price_usd": Decimal("80.00"),
                "price_pln": Decimal("320.00"),
                "rating": 4.6,
                "images": ["foot_traffic.png", "age_cohort.png"],
                "summary": "信義計畫區步行商圈人流尖峰時段（17:00-21:30）分佈、平假日客流差異與周邊交通節點人潮導流曲線。",
                "attributes": {
                    "data-coverage": "信義計畫區核心步行商圈",
                    "data-period": "2024-Q1 ~ 2026-Q2",
                    "sample-size": "3,500,000+ 筆",
                    "compliance-grade": "Tier-A (去識別化驗證)",
                    "update-frequency": "每日即時更新",
                    "data-format": "REST API & JSON Stream",
                    "license-type": "內部商業使用授權 (Internal Commercial Use)"
                }
            },
            {
                "name": "百貨週年慶人流洞察",
                "slug": "department-store-anniversary-insights",
                "price_usd": Decimal("120.00"),
                "price_pln": Decimal("480.00"),
                "rating": 4.7,
                "images": ["age_cohort.png", "industry_retail.png"],
                "summary": "彙整歷年週年慶檔期跨世代客群進店行為、停留時段熱度矩陣與消費轉換率預測模型。",
                "attributes": {
                    "data-coverage": "全台重點百貨連鎖",
                    "data-period": "2024-2026 歷年檔期",
                    "sample-size": "850,000+ 筆",
                    "compliance-grade": "Tier-A / GDPR-ready / ISO-27001",
                    "update-frequency": "每月彙總",
                    "data-format": "API / Parquet / Snowflake Data Share",
                    "license-type": "內部商業使用授權 (Internal Commercial Use)"
                }
            }
        ]

        placeholders_base = "saleor/static/placeholders/data_products"

        for p_info in products_data:
            desc_json = {
                "time": 1725140000000,
                "blocks": [
                    {"data": {"text": p_info["summary"]}, "type": "paragraph"},
                    {
                        "data": {
                            "text": "<b>數據產品特徵：</b><br/>• 涵蓋範圍：" + p_info["attributes"]["data-coverage"] +
                                    "<br/>• 採樣區間：" + p_info["attributes"]["data-period"] +
                                    "<br/>• 合規等級：" + p_info["attributes"]["compliance-grade"] +
                                    "<br/>• 更新頻率：" + p_info["attributes"]["update-frequency"]
                        },
                        "type": "paragraph"
                    }
                ],
                "version": "2.28.0"
            }

            product, created = Product.objects.update_or_create(
                slug=p_info["slug"],
                defaults={
                    "name": p_info["name"],
                    "description": desc_json,
                    "description_plaintext": p_info["summary"],
                    "category": category,
                    "product_type": product_type,
                    "rating": p_info["rating"]
                }
            )
            self.stdout.write(f"Product: {product.name} (Created: {created})")

            # Channel listing for product
            ProductChannelListing.objects.update_or_create(
                product=product,
                channel=channel_usd,
                defaults={
                    "is_published": True,
                    "visible_in_listings": True,
                    "discounted_price_amount": p_info["price_usd"]
                }
            )
            if channel_pln:
                ProductChannelListing.objects.update_or_create(
                    product=product,
                    channel=channel_pln,
                    defaults={
                        "is_published": True,
                        "visible_in_listings": True,
                        "discounted_price_amount": p_info["price_pln"]
                    }
                )

            # Create default Variant
            sku = f"DATA-{p_info['slug'].upper()[:20]}"
            variant, v_created = ProductVariant.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": "標準商業授權 (Standard License)",
                    "product": product,
                    "track_inventory": False
                }
            )
            product.default_variant = variant
            product.save(update_fields=["default_variant"])

            # Variant Channel Listing (Pricing)
            ProductVariantChannelListing.objects.update_or_create(
                variant=variant,
                channel=channel_usd,
                defaults={
                    "price_amount": p_info["price_usd"],
                    "cost_price_amount": p_info["price_usd"] * Decimal("0.3")
                }
            )
            if channel_pln:
                ProductVariantChannelListing.objects.update_or_create(
                    variant=variant,
                    channel=channel_pln,
                    defaults={
                        "price_amount": p_info["price_pln"],
                        "cost_price_amount": p_info["price_pln"] * Decimal("0.3")
                    }
                )

            # Stock
            if warehouse:
                Stock.objects.update_or_create(
                    warehouse=warehouse,
                    product_variant=variant,
                    defaults={"quantity": 99999}
                )

            # Assign Attributes
            for attr_slug, val_text in p_info["attributes"].items():
                attr = attr_objs.get(attr_slug)
                if attr:
                    val_obj = AttributeValue.objects.filter(attribute=attr, name=val_text).first()
                    if val_obj:
                        assigned_val, _ = AssignedProductAttributeValue.objects.get_or_create(
                            product=product,
                            value=val_obj
                        )

            # Assign Media
            product.media.all().delete()
            for sort_order, img_name in enumerate(p_info["images"]):
                img_path = os.path.join(placeholders_base, img_name)
                if os.path.exists(img_path):
                    with open(img_path, "rb") as f:
                        media = ProductMedia(
                            product=product,
                            alt=f"{p_info['name']} - {img_name}",
                            sort_order=sort_order
                        )
                        media.image.save(img_name, File(f), save=True)
                        self.stdout.write(f"  Attached media: {img_name}")

        self.stdout.write(self.style.SUCCESS("✓ Successfully populated InsaiVue Data Products!"))
