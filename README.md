
---

# **RUMAD 2.0**  
*Introduction to Database Systems Term Project*  
**CIIC4060/ICOM5016** | **Fall 2024**

---

<div align="center">
  <img alt="npr-logo" src="https://github.com/user-attachments/assets/5d64f86e-00eb-47bc-b46b-af8a139ba595" width="500">
</div>

---

### **Members**
| Name                      | Major                         | Role  | Email                              |
|---------------------------|-------------------------------|-------|------------------------------------|
| Sebastián A. Cruz Romero  | Computer Science & Engineering | ---   | sebastian.cruz6@upr.edu           |
| Jared Cruz                | Computer Engineering           | ---   | jared.cruz@upr.edu                |
| Perla N. Colón Marrero    | Computer Engineering           | ---   | perla.colon@upr.edu               |
| Eduardo Ramirez           | Computer Engineering           | ---   | eduardo.ramirez4@upr.edu          |
| Norely Torres Berrios     | Computer Science & Engineering | ---   | norely.torres1@upr.edu            |

---

## **Application Hostname**
- [App URL](https://nprdb-app-test-fall2024-5e22b455dcd3.herokuapp.com/)

---

## **Running the Application**

### **Step 1: Set Up Heroku Environment**
Set the required environment variables using the Heroku CLI:

```bash
heroku config:set ENV_VARIABLE=value --app nprdb-app-test-fall2024
```

### **Step 2: Run the ETL Script**
Load the data into the database:

```bash
python ETL/load.py
```

### **Step 3: Start the Application**
Run the backend application:

```bash
python -m myApp.app
```

### **Step 4: Launch the Frontend**
Run the Streamlit interface:

```bash
streamlit run myApp/frontend.py
```

---

## **How to Use**

### **1. Install Dependencies**
Install all necessary dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### **2. Navigate to the Working Directory**
Navigate to the ETL directory within the project:

```bash
cd /rumad-v2-app-no-pensamos-repetir-npr/ETL/
```

### **3. Run the ETL Script**
Execute the script to load the data into the database:

```bash
python ETL/load.py
```

### **4. Choose the Modality**
- Local development: **Enter 1**  
- Production deployment: **Enter 2** (Hosted on Heroku)

---

## **Database Connection via DataGrip**
Connect to the Heroku-hosted database using DataGrip:

1. Create a new PostgreSQL Data Source.  
2. Add the credentials provided above.  
3. Verify the connection and ensure there are no trailing spaces in the inputs.

![DataGrip Screenshot](https://github.com/user-attachments/assets/746f092b-7e23-42d8-b2f0-8d335098a861)

---

## **Important Notes**
- Always verify your database connection.  
- Test the app thoroughly after deploying any updates.  
- Credentials are subject to change; notify the team if access issues arise.

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/jqhbANi7)

---
