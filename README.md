<a id="top"></a>

# 🌍 FINAL PROJECTS — Topography Software & Sensor-Based Systems

⭐🔥 **Two Final Degree Project applications focused on topography, measurement data, and 3D visualization.**

This repository contains the software developed as part of my Final Degree Project. It includes two complementary applications related to topographic data acquisition, processing, management, and visualization.

---

## 📌 Table of Contents

- [About](#-about)
- [Projects Included](#-projects-included)
- [Technologies Used](#-technologies-used)
- [How to Start APP TFG 1](#-how-to-start-app-tfg-1)
- [How to Start APP TFG 2 — TopoSoft](#-how-to-start-app-tfg-2--toposoft)
- [Documentation](#-documentation)
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

The repository combines several technologies depending on each application:

### APP TFG 1

- Arduino IDE
- Sensor-based data acquisition
- Python
- Serial communication
- Data processing and graphical representation

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

## 📝 How to Start APP TFG 1

To run the first application, make sure the required hardware and software environment are correctly prepared.

```shell
# 1. Open the Arduino IDE

# 2. Connect the required sensors and microcontroller

# 3. Upload the Arduino sketch to the board

# 4. Run the corresponding Python script for data processing or visualization
python main.py
