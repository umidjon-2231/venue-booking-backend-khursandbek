# **Backend Developer Task: Venue Booking System**

## **Project Name: `venue-booking-backend`**

## **Overview**

Build a REST API backend for a venue/spot booking application inspired by [Bron24.uz](https://bron24.uz/). The system includes user authentication via OTP, venue management, and booking functionality with a full admin panel.

---

## **Tech Stack (Required)**

* **Language**: Python 3.11+  
* **Framework**: Django 5.0+  
* **API**: Django REST Framework  
* **Database**: PostgreSQL  
* **Cache/OTP Storage**: Redis  
* **Internationalization**: django-modeltranslation, django-parler, or similar  
* **API Documentation**: drf-spectacular, drf-yasg, or similar (Swagger UI)  
* **Containerization**: Docker with Docker Compose  
* **Optional**: Celery for async tasks

---

## **Data Models**

### **Venue**

* Name (translatable)  
* Address (translatable)  
* Description (translatable)  
* Price per hour  
* Images (list of URLs)  
* Amenities (list, translatable)  
* Active status  
* Timestamps (created, updated)

### **User**

* Phone number (unique, format: \+998XXXXXXXXX)  
* Name  
* Active status  
* Verified status  
* Timestamp (created)

### **Booking**

* User reference  
* Venue reference  
* Booking date  
* Start time  
* End time  
* Total price  
* Status (pending, confirmed, cancelled, completed)  
* Timestamps (created, updated)

---

## **API Endpoints**

### **Authentication**

| Method | Endpoint | Description |
| ----- | ----- | ----- |
| POST | `/api/auth/send-otp/` | Send OTP to phone number |
| POST | `/api/auth/verify-otp/` | Verify OTP and receive JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user profile |
| PATCH | `/api/auth/me/` | Update user profile |

### **Venues**

| Method | Endpoint | Description |
| ----- | ----- | ----- |
| GET | `/api/venues/` | List all venues with pagination and filters |
| GET | `/api/venues/{id}/` | Get single venue details |
| GET | `/api/venues/{id}/availability/` | Get available time slots for a specific date |

### **Bookings**

| Method | Endpoint | Description |
| ----- | ----- | ----- |
| GET | `/api/bookings/` | List current user's bookings |
| POST | `/api/bookings/` | Create new booking |
| GET | `/api/bookings/{id}/` | Get booking details |
| PATCH | `/api/bookings/{id}/cancel/` | Cancel a booking |

---

## **Functional Requirements**

### **OTP Authentication**

* Accept phone number and send OTP (mock SMS by logging OTP to console)  
* Store OTP in Redis with 5-minute expiration  
* Verify OTP and return JWT tokens (access and refresh)  
* Implement rate limiting: maximum 3 OTP requests per phone number per 10 minutes

### **Venue Management**

* Full CRUD operations (Create, Update, Delete restricted to admin)  
* List endpoint with pagination (10 items per page)  
* Filter by price range  
* Search by venue name  
* Multi-language support for name, address, and description fields

### **Booking System**

* Check venue availability before allowing booking  
* Prevent double booking for same time slot  
* Automatically calculate total price based on duration and hourly rate  
* Validate booking time (example: only allow bookings between 9 AM and 10 PM)  
* Users can only view and cancel their own bookings  
* Only pending or confirmed bookings can be cancelled

### **Admin Panel**

* Django admin interface for all models  
* Venue management with ability to add/edit images  
* Booking management with status update functionality  
* User management and verification  
* Translation management for multilingual fields

---

## **Internationalization (i18n)**

Support three languages in API responses:

* Uzbek \- `uz`  
* Russian \- `ru`  
* English \- `en`

Requirements:

* Accept `Accept-Language` header to determine response language  
* Translatable fields: venue name, address, description, amenities  
* Admin interface must support entering translations  
* Default language: Russian

---

## **Security Requirements**

* JWT authentication with access and refresh tokens  
* Rate limiting on authentication endpoints  
* Input validation and sanitization on all endpoints  
* Proper CORS configuration  
* All secrets stored in environment variables  
* Use Django ORM to prevent SQL injection

---

## **Docker Requirements**

Create Docker Compose setup that includes:

* Django application service  
* PostgreSQL database service  
* Redis service

Provide environment variable configuration through .env file.

---

## **Documentation Requirements**

Create a comprehensive README.md including:

1. **Project Description** \- What the API does  
2. **Tech Stack** \- List of all technologies used  
3. **Features** \- Complete list of implemented features  
4. **Architecture** \- Brief system design overview  
5. **Getting Started**  
   * Prerequisites  
   * Environment setup with .env file  
   * Running with Docker  
   * Running locally without Docker  
   * Running database migrations  
   * Creating superuser account  
6. **API Documentation**  
   * Link to Swagger/ReDoc interface  
   * Authentication flow explanation  
   * Example requests and responses for main endpoints  
7. **Admin Panel** \- How to access and use the admin interface  
8. **Internationalization** \- How translations work  
9. **Testing** \- How to run tests  
10. **AI Tools Used** \- Detailed documentation of AI assistance (see below)

---

## **AI Usage Requirement**

**Using AI tools is mandatory** for this task. You must use tools like ChatGPT, Claude, Cursor, GitHub Copilot, or similar.

Document in your README:

* Which AI tools you used  
* What specific tasks you used them for  
* Examples of prompts you used  
* Your personal evaluation of how AI assisted your development

---

## **Deliverables**

* Public GitHub repository  
* Working Docker Compose setup  
* Complete README documentation  
* Swagger UI for API documentation  
* All endpoints fully functional  
* Three languages implemented for translatable fields  
* Admin panel with translation support  
* Seed data script with minimum 10 venues  
* Basic tests for critical endpoints

---

## **Estimated Time: 1 day**

---

## **Reference**

* [Bron24.uz](https://bron24.uz/) \- Use for understanding the domain

---

**Good luck\!**

