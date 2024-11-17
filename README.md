# Group Creation AED Challenge: Datathon 2024
Project made by Aniol Garriga Torra, Cristina Teixidó Cruïlles, Gabriel Fortuny Carretero and Aleix Albaiges Torres
# Overview
This project aims to improve the team formation process at Datathon FME by building a system that matches participants based on their technical skills and hackathon goals.
Every year, Datathon FME attracts a diverse set of participants with different objectives — from winning the prize to building their portfolio, learning new skills, or connecting with fellow data enthusiasts. The goal of this project is to streamline the team formation process, making it easier and more efficient for participants to find like-minded teammates.
Rather than relying on automated team assignment, our approach focuses on matching participants using a set of distance functions that evaluate the compatibility between participants. The system takes into account a wide range of personal attributes and goals, such as:

Personal Data: Includes the participant's age, university, and dietary restrictions.

Experience and Skills: This includes their programming skills (represented as a dictionary with skill levels for each language or tool), experience level, and the number of hackathons they've participated in.

Interests and Preferences: Participants provide a list of their interests and challenges they're interested in, as well as their preferred role and team size.

Objectives: Their goals for the Datathon, such as prize hunting, portfolio building, learning new skills, or meeting new people.

Availability: The days and times the participant is available for team collaboration.

Friendship and Team Preferences: Whether participants have friends they want to register with and their preferred team size.

By using these diverse attributes, the system can apply different distance functions to evaluate participants' compatibility in both technical and non-technical areas. These functions ensure that participants are grouped into balanced, complementary teams that align not only in terms of their skills but also in their goals, interests, and availability.
