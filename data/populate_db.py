import sqlite3
import random
import faker

fake = faker.Faker()


conn = sqlite3.connect("employee_data.db")
cur = conn.cursor()

num_employees = 300

cur.execute("DELETE FROM employee_details")
cur.execute("DELETE FROM employee_work")

employee_ids = []
for _ in range(num_employees):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    phone = fake.phone_number()
    
    cur.execute(
        "INSERT INTO employee_details (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
        (first_name, last_name, email, phone),
    )
    
    employee_ids.append(cur.lastrowid) 

# Insert employee work details
departments = ["Engineering", "HR", "Finance", "Marketing", "Sales", "Operations", "IT Support"]
roles = ["Software Engineer", "Data Analyst", "Manager", "HR Specialist", "Sales Executive", "Marketing Lead"]
locations = ["New York", "San Francisco", "Los Angeles", "Chicago", "Houston", "Miami"]
projects = ["Project Alpha", "Project Beta", "Project Gamma", "Project Delta", "Project Epsilon"]

for emp_id in employee_ids:
    role = random.choice(roles)
    department = random.choice(departments)
    office_location = random.choice(locations)
    assigned_projects = random.sample(projects, random.randint(1, 3)) 
    performance_summary = fake.sentence() 
    
    cur.execute(
        "INSERT INTO employee_work (employee_id, role, department, office_location, projects, performance_summary) VALUES (?, ?, ?, ?, ?, ?)",
        (emp_id, role, department, office_location, ", ".join(assigned_projects), performance_summary),
    )

conn.commit()
conn.close()

print(f"✅ Successfully inserted {num_employees} employee records into SQLite database!")
