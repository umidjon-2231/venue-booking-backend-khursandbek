"""
Management command to seed the database with sample data.
Creates venues, users, and bookings for testing and demonstration.
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.bookings.models import Booking, BookingStatus
from apps.users.models import User
from apps.venues.models import Venue, VenueImage


class Command(BaseCommand):
    help = "Seed the database with sample venues, users, and bookings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--admin",
            action="store_true",
            help="Create a superuser admin account",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Booking.objects.all().delete()
            VenueImage.objects.all().delete()
            Venue.all_objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        self.stdout.write("Seeding database...")
        
        # Create admin user if requested
        if options["admin"]:
            admin = self.create_admin()
            if admin:
                self.stdout.write(self.style.SUCCESS("Created admin user"))
        
        # Create venues
        venues = self.create_venues()
        self.stdout.write(self.style.SUCCESS(f"Created {len(venues)} venues"))
        
        # Create users
        users = self.create_users()
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users"))
        
        # Create bookings
        bookings = self.create_bookings(venues, users)
        self.stdout.write(self.style.SUCCESS(f"Created {len(bookings)} bookings"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Database seeded successfully!"))
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SAMPLE CREDENTIALS")
        self.stdout.write("=" * 50)
        self.stdout.write("\nSample users (send OTP to login):")
        self.stdout.write("  📱 +998901234567 (Алишер Каримов)")
        self.stdout.write("  📱 +998901234568 (Малика Рахимова)")
        self.stdout.write("  📱 +998901234569 (Жамшид Усманов)")
        if options["admin"]:
            self.stdout.write("\nAdmin user:")
            self.stdout.write("  📱 +998900000000 (Admin)")
            self.stdout.write("  🔑 Access Django Admin at /admin/")

    def create_admin(self):
        """Create admin superuser."""
        admin, created = User.objects.get_or_create(
            phone_number="+998900000000",
            defaults={
                "name": "Admin",
                "is_verified": True,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        return admin if created else None

    def create_venues(self):
        """Create sample venues."""
        venues_data = [
            {
                "name_ru": "Спортивный зал 'Олимп'",
                "name_uz": "Sport zali 'Olimp'",
                "name_en": "Sports Hall 'Olymp'",
                "address_ru": "ул. Навои, 15, Ташкент",
                "address_uz": "Navoiy ko'chasi, 15, Toshkent",
                "address_en": "15 Navoi Street, Tashkent",
                "description_ru": "Современный спортивный зал с профессиональным оборудованием для тренировок и соревнований.",
                "description_uz": "Mashg'ulotlar va musobaqalar uchun professional jihozlar bilan jihozlangan zamonaviy sport zali.",
                "description_en": "Modern sports hall with professional equipment for training and competitions.",
                "price_per_hour": Decimal("150000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
                    "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800",
                ],
                "amenities": ["Душ", "Раздевалка", "Парковка", "Тренер"],
            },
            {
                "name_ru": "Конференц-зал 'Бизнес Центр'",
                "name_uz": "Konferensiya zali 'Biznes Markaz'",
                "name_en": "Conference Hall 'Business Center'",
                "address_ru": "пр. Амира Темура, 88, Ташкент",
                "address_uz": "Amir Temur shoh ko'chasi, 88, Toshkent",
                "address_en": "88 Amir Temur Avenue, Tashkent",
                "description_ru": "Современный конференц-зал на 50 человек с проектором и звуковым оборудованием.",
                "description_uz": "Proktor va ovoz uskunalari bilan jihozlangan 50 kishilik zamonaviy konferensiya zali.",
                "description_en": "Modern conference hall for 50 people with projector and sound equipment.",
                "price_per_hour": Decimal("300000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1517502884422-41eaead166d4?w=800",
                    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
                ],
                "amenities": ["WiFi", "Проектор", "Кондиционер", "Кофе-брейк"],
            },
            {
                "name_ru": "Банкетный зал 'Праздник'",
                "name_uz": "Banket zali 'Bayram'",
                "name_en": "Banquet Hall 'Celebration'",
                "address_ru": "ул. Мирабад, 45, Ташкент",
                "address_uz": "Mirabad ko'chasi, 45, Toshkent",
                "address_en": "45 Mirabad Street, Tashkent",
                "description_ru": "Роскошный банкетный зал для свадеб, юбилеев и корпоративных мероприятий до 200 гостей.",
                "description_uz": "To'ylar, yubileylar va korporativ tadbirlar uchun 200 kishilik hashamatli banket zali.",
                "description_en": "Luxurious banquet hall for weddings, anniversaries and corporate events up to 200 guests.",
                "price_per_hour": Decimal("500000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800",
                    "https://images.unsplash.com/photo-1478146896981-b80fe463b330?w=800",
                ],
                "amenities": ["Сцена", "Звук", "Освещение", "Кейтеринг", "Парковка"],
            },
            {
                "name_ru": "Коворкинг 'HUB'",
                "name_uz": "Kovorking 'HUB'",
                "name_en": "Coworking 'HUB'",
                "address_ru": "ул. Шота Руставели, 12, Ташкент",
                "address_uz": "Shota Rustaveli ko'chasi, 12, Toshkent",
                "address_en": "12 Shota Rustaveli Street, Tashkent",
                "description_ru": "Современное рабочее пространство с высокоскоростным интернетом и комфортной атмосферой.",
                "description_uz": "Yuqori tezlikdagi internet va qulay muhit bilan zamonaviy ish maydoni.",
                "description_en": "Modern workspace with high-speed internet and comfortable atmosphere.",
                "price_per_hour": Decimal("50000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800",
                    "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800",
                ],
                "amenities": ["WiFi", "Кофе", "Принтер", "Переговорная"],
            },
            {
                "name_ru": "Фотостудия 'Кадр'",
                "name_uz": "Fotostudiya 'Kadr'",
                "name_en": "Photo Studio 'Frame'",
                "address_ru": "ул. Бабура, 78, Ташкент",
                "address_uz": "Bobur ko'chasi, 78, Toshkent",
                "address_en": "78 Babur Street, Tashkent",
                "description_ru": "Профессиональная фотостудия с различными фонами и студийным светом.",
                "description_uz": "Turli fonlar va studiya yorug'ligi bilan professional fotostudiya.",
                "description_en": "Professional photo studio with various backgrounds and studio lighting.",
                "price_per_hour": Decimal("200000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=800",
                    "https://images.unsplash.com/photo-1493863641943-9b68992a8d07?w=800",
                ],
                "amenities": ["Студийный свет", "Фоны", "Гримерка", "Реквизит"],
            },
            {
                "name_ru": "Теннисный корт 'Ace'",
                "name_uz": "Tennis korti 'Ace'",
                "name_en": "Tennis Court 'Ace'",
                "address_ru": "ул. Буюк Ипак Йули, 156, Ташкент",
                "address_uz": "Buyuk Ipak yo'li, 156, Toshkent",
                "address_en": "156 Great Silk Road, Tashkent",
                "description_ru": "Крытый теннисный корт с профессиональным покрытием.",
                "description_uz": "Professional qoplamali yopiq tennis korti.",
                "description_en": "Indoor tennis court with professional surface.",
                "price_per_hour": Decimal("120000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800",
                    "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=800",
                ],
                "amenities": ["Раздевалка", "Душ", "Аренда ракеток", "Тренер"],
            },
            {
                "name_ru": "Танцевальный зал 'Ритм'",
                "name_uz": "Raqs zali 'Ritm'",
                "name_en": "Dance Hall 'Rhythm'",
                "address_ru": "ул. Чиланзар, 22, Ташкент",
                "address_uz": "Chilanzor ko'chasi, 22, Toshkent",
                "address_en": "22 Chilanzar Street, Tashkent",
                "description_ru": "Просторный танцевальный зал с зеркалами и профессиональным полом.",
                "description_uz": "Ko'zgular va professional pol bilan keng raqs zali.",
                "description_en": "Spacious dance hall with mirrors and professional floor.",
                "price_per_hour": Decimal("100000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1508807526345-15e9b5f4eaff?w=800",
                    "https://images.unsplash.com/photo-1594737625785-a6cbdabd333c?w=800",
                ],
                "amenities": ["Зеркала", "Звук", "Раздевалка", "Кондиционер"],
            },
            {
                "name_ru": "Йога-студия 'Гармония'",
                "name_uz": "Yoga-studiya 'Garmoniya'",
                "name_en": "Yoga Studio 'Harmony'",
                "address_ru": "ул. Саларская, 8, Ташкент",
                "address_uz": "Salar ko'chasi, 8, Toshkent",
                "address_en": "8 Salar Street, Tashkent",
                "description_ru": "Уютная студия для занятий йогой и медитацией в спокойной атмосфере.",
                "description_uz": "Tinch muhitda yoga va meditatsiya mashg'ulotlari uchun qulay studiya.",
                "description_en": "Cozy studio for yoga and meditation classes in a calm atmosphere.",
                "price_per_hour": Decimal("80000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800",
                    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800",
                ],
                "amenities": ["Коврики", "Реквизит", "Раздевалка", "Чай"],
            },
            {
                "name_ru": "Караоке-клуб 'Звезда'",
                "name_uz": "Karaoke-klub 'Yulduz'",
                "name_en": "Karaoke Club 'Star'",
                "address_ru": "ул. Ташкентская, 100, Ташкент",
                "address_uz": "Toshkent ko'chasi, 100, Toshkent",
                "address_en": "100 Tashkent Street, Tashkent",
                "description_ru": "VIP комната для караоке с профессиональным звуком на 15 человек.",
                "description_uz": "15 kishilik professional ovozli VIP karaoke xonasi.",
                "description_en": "VIP karaoke room with professional sound for 15 people.",
                "price_per_hour": Decimal("250000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
                    "https://images.unsplash.com/photo-1598387993281-cecf8b71a8f8?w=800",
                ],
                "amenities": ["Звук", "Микрофоны", "Бар", "Кальян"],
            },
            {
                "name_ru": "Футбольное поле 'Голеадор'",
                "name_uz": "Futbol maydoni 'Goleador'",
                "name_en": "Football Field 'Goleador'",
                "address_ru": "ул. Юнусабадская, 200, Ташкент",
                "address_uz": "Yunusobod ko'chasi, 200, Toshkent",
                "address_en": "200 Yunusabad Street, Tashkent",
                "description_ru": "Мини-футбольное поле с искусственным газоном для игр 5x5.",
                "description_uz": "5x5 o'yinlar uchun sun'iy maysali mini-futbol maydoni.",
                "description_en": "Mini football field with artificial turf for 5v5 games.",
                "price_per_hour": Decimal("180000.00"),
                "images": [
                    "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=800",
                    "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800",
                ],
                "amenities": ["Раздевалка", "Душ", "Мячи", "Манишки", "Освещение"],
            },
        ]

        venues = []
        for data in venues_data:
            venue, created = Venue.all_objects.get_or_create(
                name_ru=data["name_ru"],
                defaults={
                    "name": data["name_ru"],
                    "name_uz": data["name_uz"],
                    "name_en": data["name_en"],
                    "address": data["address_ru"],
                    "address_ru": data["address_ru"],
                    "address_uz": data["address_uz"],
                    "address_en": data["address_en"],
                    "description": data["description_ru"],
                    "description_ru": data["description_ru"],
                    "description_uz": data["description_uz"],
                    "description_en": data["description_en"],
                    "price_per_hour": data["price_per_hour"],
                    "images": data["images"],
                    "amenities": data["amenities"],
                    "is_active": True,
                }
            )
            venues.append(venue)
        
        return venues

    def create_users(self):
        """Create sample users."""
        users_data = [
            {
                "phone_number": "+998901234567",
                "name": "Алишер Каримов",
                "is_verified": True,
            },
            {
                "phone_number": "+998901234568",
                "name": "Малика Рахимова",
                "is_verified": True,
            },
            {
                "phone_number": "+998901234569",
                "name": "Жамшид Усманов",
                "is_verified": True,
            },
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                phone_number=data["phone_number"],
                defaults={
                    "name": data["name"],
                    "is_verified": data["is_verified"],
                }
            )
            users.append(user)
        
        return users

    def create_bookings(self, venues, users):
        """Create sample bookings with various statuses and dates."""
        if not venues or not users:
            return []

        today = date.today()
        
        bookings_data = [
            # ========== Future bookings (PENDING) ==========
            {
                "user": users[0],
                "venue": venues[0],  # Sports Hall
                "booking_date": today + timedelta(days=1),
                "start_time": time(10, 0),
                "end_time": time(12, 0),
                "status": BookingStatus.PENDING,
            },
            {
                "user": users[1],
                "venue": venues[1],  # Conference Hall
                "booking_date": today + timedelta(days=2),
                "start_time": time(14, 0),
                "end_time": time(17, 0),
                "status": BookingStatus.PENDING,
            },
            {
                "user": users[2],
                "venue": venues[4],  # Photo Studio
                "booking_date": today + timedelta(days=3),
                "start_time": time(11, 0),
                "end_time": time(14, 0),
                "status": BookingStatus.PENDING,
            },
            {
                "user": users[0],
                "venue": venues[7],  # Yoga Studio
                "booking_date": today + timedelta(days=5),
                "start_time": time(9, 0),
                "end_time": time(10, 0),
                "status": BookingStatus.PENDING,
            },
            
            # ========== Future bookings (CONFIRMED) ==========
            {
                "user": users[0],
                "venue": venues[2],  # Banquet Hall
                "booking_date": today + timedelta(days=3),
                "start_time": time(18, 0),
                "end_time": time(22, 0),
                "status": BookingStatus.CONFIRMED,
            },
            {
                "user": users[2],
                "venue": venues[3],  # Coworking
                "booking_date": today + timedelta(days=4),
                "start_time": time(9, 0),
                "end_time": time(13, 0),
                "status": BookingStatus.CONFIRMED,
            },
            {
                "user": users[1],
                "venue": venues[9],  # Football Field
                "booking_date": today + timedelta(days=6),
                "start_time": time(19, 0),
                "end_time": time(21, 0),
                "status": BookingStatus.CONFIRMED,
            },
            {
                "user": users[0],
                "venue": venues[5],  # Tennis Court
                "booking_date": today + timedelta(days=7),
                "start_time": time(16, 0),
                "end_time": time(18, 0),
                "status": BookingStatus.CONFIRMED,
            },
            
            # ========== Past bookings (COMPLETED) ==========
            {
                "user": users[0],
                "venue": venues[4],  # Photo Studio
                "booking_date": today - timedelta(days=2),
                "start_time": time(15, 0),
                "end_time": time(18, 0),
                "status": BookingStatus.COMPLETED,
            },
            {
                "user": users[1],
                "venue": venues[5],  # Tennis Court
                "booking_date": today - timedelta(days=5),
                "start_time": time(10, 0),
                "end_time": time(12, 0),
                "status": BookingStatus.COMPLETED,
            },
            {
                "user": users[2],
                "venue": venues[8],  # Karaoke
                "booking_date": today - timedelta(days=7),
                "start_time": time(20, 0),
                "end_time": time(22, 0),
                "status": BookingStatus.COMPLETED,
            },
            {
                "user": users[0],
                "venue": venues[6],  # Dance Hall
                "booking_date": today - timedelta(days=10),
                "start_time": time(14, 0),
                "end_time": time(16, 0),
                "status": BookingStatus.COMPLETED,
            },
            {
                "user": users[1],
                "venue": venues[2],  # Banquet Hall
                "booking_date": today - timedelta(days=14),
                "start_time": time(17, 0),
                "end_time": time(22, 0),
                "status": BookingStatus.COMPLETED,
            },
            
            # ========== Cancelled bookings ==========
            {
                "user": users[2],
                "venue": venues[6],  # Dance Hall
                "booking_date": today + timedelta(days=1),
                "start_time": time(16, 0),
                "end_time": time(18, 0),
                "status": BookingStatus.CANCELLED,
            },
            {
                "user": users[1],
                "venue": venues[0],  # Sports Hall
                "booking_date": today - timedelta(days=3),
                "start_time": time(18, 0),
                "end_time": time(20, 0),
                "status": BookingStatus.CANCELLED,
            },
        ]

        bookings = []
        for data in bookings_data:
            # Check if similar booking exists
            exists = Booking.objects.filter(
                venue=data["venue"],
                booking_date=data["booking_date"],
                start_time=data["start_time"],
            ).exists()
            
            if not exists:
                booking = Booking.objects.create(**data)
                bookings.append(booking)
        
        return bookings
