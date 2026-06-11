<a id="top"></a>

# 🌍 FINAL PROJECTS — Topography Software & Sensor-Based Systems

⭐🔥 **Two Final Degree Project applications focused on topography, measurement data, and 3D visualization.**

This repository contains the software developed as part of my Final Degree Project. It includes two complementary applications related to topographic data acquisition, processing, management, and visualization.

---

## 📌 Table of Contents

- [About](#-about)
- [Projects Included](#-projects-included)
- [Technologies Used](#-technologies-used)
- [Repository Structure](#-repository-structure)
- [How to Start APP TFG 1](#-how-to-start-app-tfg-1)
- [How to Start APP TFG 2 — TopoSoft](#-how-to-start-app-tfg-2--toposoft)
- [Main Features](#-main-features)
- [Documentation](#-documentation)
- [Project Status](#-project-status)
- [Contact](#%EF%B8%8F-contact)

---

## 🚀 About

**FINAL PROJECTS** is a repository containing the two applications developed as part of my Final Degree Project, both focused on the field of topography and the management of measurement data.

The first application focuses on the design of a **sensor-based topographic system**, integrating hardware and software components for data capture, processing, and representation.

The second application, **TopoSoft**, is a local desktop tool for managing and visualizing basic topographic measurements. It allows users to create measurements, register polygonal points, add radiations associated with base stations, store the information locally, and represent the resulting paths in a three-dimensional environment.

The repository is organized to document the technical development carried out, facilitate the execution of both applications, and maintain a clear structure of the source code, required resources, and project documentation.

[Back to top](#top)

---

## 🧩 Projects Included

### 📡 APP TFG 1 — Sensor-Based Topographic System

The first application is related to the development of a topographic system based on sensors. Its purpose is to capture and process measurement data obtained from hardware components, such as inertial sensors and distance sensors, and represent the collected information through software tools.

Main objectives:

- Capture topographic-related data from sensors.
- Process raw measurement data.
- Explore the use of low-cost hardware in topographic environments.
- Provide a technical basis for future improvements involving physical data acquisition.

---

### 🗺️ APP TFG 2 — TopoSoft

**TopoSoft** is a local desktop application designed to manage and visualize basic topographic measurements.

Main features:

- Create and manage independent measurements.
- Register polygonal points using distance, inclination, and azimuth.
- Add radiations associated with base points.
- Store all information locally using SQLite.
- Display the polygonal path and radiations in a 3D interactive view.
- Run as a desktop application using Electron.

[Back to top](#top)

---

## 🛠️ Technologies Used

The repository combines several technologies depending on each application.

### APP TFG 1

- Arduino IDE
- Sensor-based data acquisition
- Python
- Serial communication
- Data processing
- Graphical representation

### APP TFG 2 — TopoSoft

- Electron
- HTML5
- CSS3
- JavaScript
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Plotly.js
- Node.js / npm

[Back to top](#top)

---

## 📁 Repository Structure

The repository is organized to separate the different components of the project.

```text
app_tfg_1/
│
├── test examples/
│   ├── bno055.ino
│   ├── laser.ino
│   ├──
│   └── 
│
├──bno055.ino
├──scriptPuntos.py
│ 
app_tfg_2/
│
├── html/
│   ├── index.html
│   ├── grafica.html
│   └── ayuda.html
│
├── pybackend/
│   ├── app.py
│   ├── requirements.txt
│   └── puntos.db
│
├── main.js
├── start.js
├── package.json
├── package-lock.json
├── README.md
└── .gitignore
```

Main components:

- `html/index.html`: main interface for managing measurements, polygonal points, and radiations.
- `html/grafica.html`: 3D visualization screen for representing polygonal paths and radiations.
- `html/ayuda.html`: help screen for the user.
- `pybackend/app.py`: FastAPI backend, data models, validation rules, API endpoints, and database access.
- `pybackend/puntos.db`: local SQLite database.
- `main.js`: Electron main process.
- `start.js`: script used to start the backend and then launch Electron.
- `package.json`: Node.js and Electron project configuration.
- `requirements.txt`: Python backend dependencies.

[Back to top](#top)

---

## 📝 How to Start APP TFG 1

To run the first application, make sure the required hardware and software environments are correctly prepared. If you do not have any hardware, you can run the application in simulation mode.

```shell
# 1. Open the Arduino IDE

# 2. Connect the required sensors and microcontroller

# 3. Upload the Arduino sketch to the board

# 4. Run the corresponding Python script for data processing or visualization
python main.py
```

> Note: the exact execution process may depend on the hardware configuration and the folder structure used for APP TFG 1.

[Back to top](#top)

---

## 📝 How to Start APP TFG 2 — TopoSoft

TopoSoft is built with Electron for the desktop interface and FastAPI for the local backend.

### 1. Clone the repository

```shell
git clone https://github.com/Gu1ll07/TFG.git
cd TFG
```

### 2. Install backend dependencies

```shell
cd pybackend

python -m venv .venv
```

Activate the virtual environment:

```shell
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install Python dependencies:

```shell
pip install -r requirements.txt
```

### 3. Install Electron dependencies

```shell
cd ..
npm install
```

### 4. Start the application

```shell
npm start
```

The application starts the local backend and opens the Electron desktop interface.

Backend local URL:

```text
http://127.0.0.1:8000
```

[Back to top](#top)

---

## 🔌 Backend API

TopoSoft includes a local FastAPI backend that manages measurements, polygonal points, and radiations.

Main backend routes:

```text
GET     /health

GET     /medidas
POST    /medidas
GET     /medidas/{mid}
PUT     /medidas/{mid}
DELETE  /medidas/{mid}

GET     /puntos
POST    /puntos
GET     /puntos/{pid}
PUT     /puntos/{pid}
DELETE  /puntos/{pid}

GET     /radiaciones
POST    /radiaciones
GET     /radiaciones/{rid}
PUT     /radiaciones/{rid}
DELETE  /radiaciones/{rid}
```

These endpoints allow the application to perform CRUD operations and maintain persistent local data through SQLite.

[Back to top](#top)

---

## ✨ Main Features

### Measurement Management

TopoSoft allows users to create, select, consult, and delete independent topographic measurements. Each measurement acts as a working unit that groups polygonal points and radiations.

### Polygonal Points

Users can register polygonal points by entering:

- Label
- Distance
- Inclination
- Azimuth

These values are stored in the local database and later used to calculate the 3D path.

### Radiations

The application allows users to add radiations associated with a base point belonging to the polygonal path. Each radiation is calculated from its corresponding base station.

### Local Persistence

All project data is stored locally using SQLite, allowing users to keep their measurements without depending on an external server.

### 3D Visualization

TopoSoft transforms topographic values into relative Cartesian coordinates and represents the polygonal path and its radiations using Plotly.js.

### Desktop Environment

The interface is executed as a desktop application using Electron, providing a local application experience while keeping the flexibility of web technologies.

[Back to top](#top)

---

## 📚 Documentation

The repository includes the source code and documentation related to the development of both applications.

Recommended documentation sections:

- Final Degree Project report.
- Technical design and architecture.
- Backend API structure.
- Data model.
- User interface design.
- Testing and validation.
- Future improvements.

[Back to top](#top)

---

## 📌 Project Status

The project currently provides a functional version of TopoSoft, including:

- Local desktop execution.
- Backend API with FastAPI.
- SQLite local database.
- Management of measurements, points, and radiations.
- 3D visualization of topographic paths.
- Basic validation and testing of the main workflows.

Future improvements may include:

- Advanced export and import options.
- Improved help documentation.
- Enhanced topographic calculations.
- Automated testing.
- Multiplatform packaging.
- Integration with physical data acquisition devices.

[Back to top](#top)

---

## 🗨️ Contact

For more details about the project or any information regarding this repository, feel free to contact me.

- **Email:** [guillobermejo@gmail.com](mailto:guillobermejo@gmail.com)

You can also check my LinkedIn profile:

<a href="https://www.linkedin.com/in/juan-guillo-bermejo-a5b940205/" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30" />
</a>

---

## 🎓 Final Degree Project

Developed by **Juan Guillo Bermejo** as part of the Final Degree Projects in Software Engineering and Computer Engineering.

[Back to top](#top)
