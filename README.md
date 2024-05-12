Project Overview

Project Name: Django Vendor Management System with Performance Metrics

Objective:
The objective of the project is to develop a Vendor Management System using Django and Django REST Framework. This system will handle vendor profiles, track purchase orders, and calculate vendor performance metrics.

Key Features:

User Authentication: Users can register as either a buyer or a vendor and log in securely to access the system.
Vendor Management: Vendors can create and manage their profiles, including contact details and address information.
Purchase Order Tracking: The system allows buyers to create purchase orders, which vendors can then acknowledge, issue, and complete.
Performance Metrics Calculation: The system calculates various performance metrics for vendors, including on-time delivery rate, quality rating average, average response time, and fulfillment rate.
Historical Performance Tracking: Historical performance metrics are recorded over time to track vendor performance trends.
Technology Stack:

Django: Backend framework for building web applications using Python.
Django REST Framework: Powerful and flexible toolkit for building Web APIs in Django.
Swagger: API documentation tool for describing, producing, consuming, and visualizing RESTful web services.
Implementation Highlights:

User Model: Custom user model implemented to support both buyers and vendors with different user types.
API Endpoints: Various endpoints implemented to handle user authentication, vendor management, purchase order tracking, and performance metrics calculation.
Swagger Documentation: Swagger used to generate interactive API documentation, making it easy for developers to understand and test the endpoints.
Filters and Pagination: Implemented filters and pagination for list pages to enhance usability and performance. Users can filter data based on specific criteria and navigate through large datasets efficiently.
This project aims to streamline vendor management processes, improve transparency and accountability, and facilitate data-driven decision-making by providing valuable insights into vendor performance.



Setting Up the Project:

1. Clone the Repository:
git clone <repository-url>

2. Navigate to Project Directory:
cd Vendor_Management
run ls to check if there is any file named manage.py , if it is there then you are in right directory.

3.Create and Activate Virtual Environment:
For MAC/Linux:
python3 -m venv venv
source venv/bin/activate
For Windows:
python -m venv venv
venv\Scripts\activate

4.Install Dependencies:
pip install -r requirements.txt

5. Run Migrations:(Optional)- Only if it is asking for migrations:
python manage.py migrate

6. Run the Development Server:
python manage.py runserver

7. Access the API Documentation:

Open a web browser and go to http://localhost:8000/swagger/ to access the Swagger documentation for testing and exploring the APIs.

8. Explore the APIs:

Use the Swagger documentation to explore the available endpoints and interact with the APIs for vendor management, purchase order tracking, and performance metrics calculation.

9. Test Using the Vendor Management System!

You have successfully set up the project. Start creating vendor profiles, managing purchase orders, and tracking vendor performance metrics using the Django Vendor Management System.

10. How to access APIs:
First of all you need to create accounts(signup) of users(buyer and vendor in our cases). Then after Signup , login that user and you will get the access token in response . Now for each api you need enter that token like : "Bearer <generated_token>".

List of Endpoints:

Authentication
POST /api/login/: User login endpoint.

Buyer CRUD
POST /api/buyers/signup/: Buyer signup endpoint.
GET /api/buyers/by_id/: Retrieve buyer profile endpoint.
GET /api/buyers/: List buyers endpoint.

Buyer Purchase Order
POST /api/buyers/purchase_orders/: Create purchase order endpoint.
POST /api/buyers/purchase_orders/cancel/<int:purchase_order_id>/: Cancel purchase order endpoint.
POST /api/buyers/purchase_orders/rate/<int:purchase_order_id>/: Rate purchase order endpoint.

Vendor CRUD
POST /api/vendors/signup/: Vendor signup endpoint.
GET /api/vendors/by_id/: Retrieve vendor profile endpoint.
GET /api/vendors/: List vendors endpoint.

Vendor Items
POST /api/vendors/items/: Create item endpoint.
PUT /api/vendors/items/update/: Update item endpoint.
DELETE /api/vendors/items/delete/<int:item_id>/: Delete item endpoint.

Vendor Purchase Order
GET /api/vendors/orders/: List purchase orders endpoint.
POST /api/vendors/purchase_orders/<int:purchase_order_id>/issue/: Issue purchase order endpoint.
POST /api/vendors/purchase_orders/<int:purchase_order_id>/acknowledge/: Acknowledge purchase order endpoint.
POST /api/vendors/purchase_orders/<int:purchase_order_id>/complete/: Complete purchase order endpoint.

Vendor Performance
GET /api/vendors/performance/: Get vendor performance metrics endpoint.
GET /api/vendors/historical-performance/: Get historical performance metrics endpoint.

Request and Response Formats
Request Format: Requests are made using HTTP methods (GET, POST, PUT, DELETE) to specific endpoints. The request may include parameters in the URL, query parameters, request body, or headers, depending on the endpoint.
Response Format: Responses are returned in JSON format. Each response includes a response_message field describing the outcome of the request and a response_data field containing relevant data. Additionally, the response status code indicates the success or failure of the request.

Authentication
JWT Token: Authentication for accessing API endpoints is handled using JSON Web Tokens (JWT). Users are required to authenticate by including a valid JWT token in the Authorization header of the request. Without authentication, access to most endpoints is restricted.
Note on Filters and Pagination

Filters: Some list endpoints support filtering by specific parameters, such as vendor name or item name. Users can include filter parameters in the query string of the URL to narrow down the results.
Pagination: List endpoints are paginated to improve performance and manage large datasets. Users can specify the page number and page size in the query string to navigate through the paginated results.


For any issue in the project setup or accessing the APIs , please contact me directly .
Thank You.
