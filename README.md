<img src="FT-logo128.jpg" alt="FEAT Logo" width="80" height="80">

# Feat
Feedback Experiment Aansturing Tool

Create fast feedback messages based on your own prewritten feedback file and add personalised feedback per student. Feat requires you to import a list of student, which allows you to create feedback messages with personal salutation. It also gives you the opportunity to easily switch between the feedback text for all students in your group. You can save the .feat file and continue to provide feedback. With a single click the feedback messages is copied to your clipboard and ready to send to your students using the communication method of your choice. 

## Features
* Import prewritten feedback
* Import student names
* Switch between feedback messages of students
* Have personal salutations
* Add personalised feedback for each feedback section
* Add personalised feedback in a general section
* Add general complimentary close
* Save the feedback messages
* Copy the feedback messages to the clipboard

## Screenshots
Select **file > new**, a new window appears. 

![Screenshot new file](docs/images/screenshot_new.png)

* Select the location and give the name of the new file.
* Select the file with student names.
* select the file with feedback.

Select **file > open** to open a .feat file. 

![Screenshot new file](docs/images/screenshot_open.png)

## Install
Clone the repository.

Create a new conda environment with python
```
conda create -n feat python
``` 
Activate the new conda enviornment
```
conda activate feat
```
Install Feat with poetry install
```
poetry install
```
Open Feat with ft. 
```
ft.
```