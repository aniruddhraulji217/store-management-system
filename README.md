# Store Management System

A Python-based application designed to manage and streamline operations for retail stores. The system includes comprehensive features for inventory management, sales tracking, purchase handling, and user management, making it an ideal solution for businesses of all sizes.

---

## Features

### Core Functionalities
1. **Inventory Management**
   - Add, update, and delete products.
   - Track stock levels and identify low-stock items.
   - Export inventory reports to CSV for external use.
   - Maintain an audit log for tracking changes.

2. **Sales Management**
   - Process sales transactions and record sales data.
   - View revenue reports, such as revenue for the last 30 days.
   - Generate bill and can convert in PDF also.

3. **Purchase Management**
   - Record and manage purchases.
   - Maintain supplier information.
   - View detailed purchase history and reports.

4. **User Management**
   - Manage user accounts with role-based access control (Admin/Staff).
   - Add, edit, delete, and search users.
   - set reset Password also.

### Additional Features
- **Dashboard**:
  - Admin dashboard includes business insights such as:
    - Total revenue (last 30 days).
    - Inventory value.
    - Low stock items.
    - Total customers.

- **Role-Based Access**:
  - Admins have full access to all features.
  - Staff members have restricted access.

- **Audit Logs**:
  - Track and view detailed logs for inventory and purchase changes.

---

## Technologies Used

- **Programming Language**: Python
- **Database**: MySQL
- **GUI Framework**: Tkinter

---

## File Structure

- **`main.py`**: Entry point of the application. It initializes the GUI and manages navigation between various modules.
- **`admin_dashboard.py`**: Manages the admin-specific dashboard and business statistics.
- **`pages/`**: Contains modules for different features:
  - `inventory_management.py`: Handles inventory-related operations.
  - `sales_management.py`: Manages sales operations.
  - `user_management.py`: Manages user accounts and roles.
  - `purchase_management.py`: Handles purchase and supplier management.

---

## Setup and Installation

### Prerequisites
Ensure the following are installed on your system:
- Python 3.x
- MySQL Server
- `pip` (Python package manager)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/aniruddhraulji217/store-management-system.git
   cd store-management-system
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Set up the MySQL database:
   - Create a database in MySQL (e.g., inventory_db).
   - Import the database schema
4. Update database credentials:
   -Open files such as inventory_management.py, purchase_management.py, or other modules.
   -Update the database connection details (host, user, password, database) as per your MySQL setup.
5. Run the application:
   ```bash
    python main.py

---

## Usage

1. Launch the application.
2. Log in using admin or staff credentials.
3. Navigate through the dashboard to access features like inventory, sales, purchases, and user management.
4. Use the export and audit log features for enhanced reporting.
5. Admin users can reset passwords and access advanced functionalities.

---

## Contribution Guidelines

We welcome contributions! Here's how you can help:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description, and ensure to follow the project's coding style.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Contact

For questions, suggestions, or feedback, feel free to reach out:
- **GitHub**: [aniruddhraulji217](https://github.com/aniruddhraulji217)
