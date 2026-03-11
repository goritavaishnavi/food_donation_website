Food Donation Management System

A Role-Based Food Donation Management Web Application designed to reduce food waste by connecting Donors, NGOs, and Volunteers through a centralized digital platform.

The system allows donors to submit surplus food donations, NGOs to manage requests, and volunteers to deliver food efficiently to those in need.
**📌 Project Overview**

Food waste is a significant global problem, while millions of people suffer from hunger.
This project provides a web-based solution to bridge the gap between surplus food providers and organizations that distribute food to needy communities.

The platform enables real-time donation tracking, role-based dashboards, and location-based pickup coordination.

**🚀 Features**
👤 Donor Module

Create food donation

Upload food details

Provide quantity and location

View donation history

Track donation status

Profile with total donation count

**🏢 NGO Module**

View available donations

Accept donation requests

Assign volunteers

Track delivery status
**🚚 Volunteer Module**

View assigned deliveries

Pickup food from donors

Deliver food to NGOs

Update delivery status

**🛠 Admin Module**

Manage users

Monitor donations

Approve or reject donations

View analytics dashboard

**📍 Location Features**

GPS location detection

Reverse geocoding (coordinates → area name)

Map-based donation visualization

**📊 Donation Workflow**
Donor Creates Donation
        ↓
Donation Status = Pending
        ↓
NGO Approves Request
        ↓
Volunteer Assigned
        ↓
Food Picked Up
        ↓
Food Delivered

**💻 Technology Stack**
**Frontend**

HTML

CSS

JavaScript

Responsive UI Design

**Backend**

Python Flask

REST API architecture

**Database**

SQLite

APIs Used

OpenStreetMap Reverse Geocoding API

Browser Geolocation API

** Project Structure**
food-donation-system/

backend/
│
├── app.py
├── database.db
│
├── templates/
│   └── donor.html
│
├── static/
│   └── donor.css

**README.md**
⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/yourusername/food-donation-system.git
2️⃣ Navigate to project folder
cd food-donation-system/backend
3️⃣ Install dependencies
pip install flask
4️⃣ Run the backend server
python app.py
5️⃣ Open in browser
http://127.0.0.1:5000/donor
**🧪 Testing the Application**

Open donor dashboard

Fill donation details

Submit donation

Verify donation appears in history table

**Security Features**

Input validation

Secure backend API handling

Role-based system design

**Future Improvements**

NGO and Volunteer dashboards

Real-time notifications

Mobile application

AI-based food demand prediction

Route optimization for volunteers

Admin analytics dashboard

**Use Cases**

Restaurants donating surplus food

Wedding halls donating leftover food

NGOs collecting food donations

Volunteers delivering food

**👨‍💻 Contributors**

Vaishnavi Reddy

**📜 License**

This project is created for academic and educational purposes.
