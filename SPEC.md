# Food Donation Website - Specification Document

## 1. Project Overview

**Project Name:** FoodShare - Food Donation Platform

**Project Type:** Full-stack Web Application

**Core Functionality:** A comprehensive food donation platform connecting donors with NGOs through volunteers, featuring role-based dashboards, real-time notifications, AI chatbot, and rating system.

**Target Users:** 
- Donors (individuals, restaurants, hotels, event organizers)
- NGOs (non-governmental organizations working for food security)
- Volunteers (individuals who help transport food)
- Admin (platform administrators)

---

## 2. Technology Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite with SQLAlchemy
- **Authentication:** Flask-Login
- **API:** RESTful endpoints

### Frontend
- **HTML5:** Semantic HTML
- **CSS3:** Custom CSS with responsive design
- **JavaScript:** Vanilla JS for interactivity
- **Chatbot:** Rule-based AI chatbot

### Database Schema

#### Users Table
- id, username, email, password_hash, role (donor/ngo/volunteer/admin), 
- bio, profile_image, contact_no, created_at

#### Donations Table
- id, donor_id, food_type, quantity, expiry_date, pickup_location, 
- pickup_time, status, created_at

#### Requests Table
- id, donation_id, ngo_id, status, requested_at

#### Volunteers Table
- id, user_id, availability, assigned_donations

#### Ratings Table
- id, donor_id, ngo_id, rating, feedback, photos, created_at

#### Notifications Table
- id, user_id, message, is_read, created_at

---

## 3. UI/UX Specification

### Color Palette
- **Primary:** #2E7D32 (Forest Green - represents freshness)
- **Secondary:** #FF6F00 (Amber - warmth, food)
- **Accent:** #00ACC1 (Cyan - trust)
- **Background:** #FAFAFA (Light gray)
- **Dark Background:** #1A1A2E (Deep navy)
- **Card Background:** #FFFFFF
- **Text Primary:** #212121
- **Text Secondary:** #757575
- **Success:** #4CAF50
- **Warning:** #FFC107
- **Error:** #F44336

### Typography
- **Headings:** 'Playfair Display', serif
- **Body:** 'Poppins', sans-serif
- **Font Sizes:**
  - H1: 2.5rem
  - H2: 2rem
  - H3: 1.5rem
  - Body: 1rem
  - Small: 0.875rem

### Layout Structure

#### Landing Page
- Hero section with animated food illustrations
- Features section (How it works)
- Statistics counter
- Testimonials
- Call to action
- Footer with links

#### Authentication Pages
- Login form with role selection
- Registration with role-based fields
- Password recovery

#### Dashboard Layout (All Roles)
- Sidebar navigation (collapsible on mobile)
- Top header with notifications bell and profile
- Main content area with cards
- Quick action buttons

### Components

#### Cards
- Donation cards with food image placeholder
- Profile cards with avatar
- Stats cards with icons
- Notification cards

#### Forms
- Input fields with floating labels
- Dropdown selects
- Date/time pickers
- File upload for profile images
- Rich text area for descriptions

#### Buttons
- Primary: Green filled
- Secondary: Outlined
- Danger: Red for delete actions
- Icon buttons for actions

#### Chatbot
- Floating chat button (bottom-right)
- Chat window with message bubbles
- Typing indicator
- Quick reply suggestions

---

## 4. Functionality Specification

### Authentication System
- Email/password registration
- Role selection (Donor, NGO, Volunteer, Admin)
- Login with role-based redirect
- Session management
- Logout functionality

### Donor Features
- Post donation (food type, quantity, expiry, location, time)
- View donation history
- See incoming requests from NGOs
- Accept/reject requests
- View ratings and feedback
- Profile management

### NGO Features
- Receive notifications for new donations
- Request food from donors
- View request history
- Rate and give feedback to donors
- Upload feedback photos
- Profile management

### Volunteer Features
- View assigned donations
- Update delivery status
- View delivery history
- Profile management

### Admin Features
- View all users
- Assign volunteers to donations
- View all donations and requests
- Platform statistics
- User management

### Chatbot Features
- Answer FAQs about donation process
- Guide users through donation posting
- Explain NGO registration
- Volunteer information
- Contact support
- General queries

### Rating & Feedback System
- NGOs can rate donors (1-5 stars)
- Text feedback
- Photo upload for completed donations
- Display ratings on donor profiles

### Notification System
- Real-time notifications for:
  - New donation posted (to NGOs)
  - Request received (to donors)
  - Request accepted/rejected
  - Volunteer assigned
  - Delivery completed

---

## 5. Page Structure

1. **index.html** - Landing page
2. **login.html** - Login page
3. **register.html** - Registration page
4. **donor_dashboard.html** - Donor dashboard
5. **ngo_dashboard.html** - NGO dashboard
6. **volunteer_dashboard.html** - Volunteer dashboard
7. **admin_dashboard.html** - Admin dashboard
8. **post_donation.html** - Post new donation
9. **donation_details.html** - View donation details
10. **request_food.html** - NGO requests food
11. **profile.html** - User profile
12. **history.html** - Activity history
13. **notifications.html** - All notifications

---

## 6. Acceptance Criteria

### Visual Checkpoints
- [ ] Landing page loads with hero animation
- [ ] All role dashboards have consistent sidebar
- [ ] Chatbot appears as floating button
- [ ] Forms have proper validation styling
- [ ] Cards display properly on all screen sizes
- [ ] Profile images display correctly

### Functional Checkpoints
- [ ] User can register with role selection
- [ ] User can login and sees role-based dashboard
- [ ] Donor can post donation
- [ ] NGO receives notification and can request
- [ ] Admin can assign volunteers
- [ ] Rating system works with photos
- [ ] Chatbot responds to queries
- [ ] Profile can be updated
- [ ] History displays all activities

### Performance
- [ ] Pages load within 3 seconds
- [ ] Responsive on mobile devices
- [ ] Database queries optimized

