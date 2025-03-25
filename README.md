# Secure-Medical-Records-Management-Using-Blockchain

A blockchain based medical record management system where the patient has complete access over who their data can be accessed by. Doctors need to request the patient for their access and the access can be revoked by the patient. The doctor's access to the patient's record results in a log being generated for the patient where they can see the date along with time when the doctor accessed the patient's records.

To run the docker file go to the root folder of the project in the terminal and then type the following command:
```docker-compose up --build```

**During the 1st time it shall take some time, since it shall download the images required for running it.**

To delete/remove the containers just use:
```docker-compose down -v```

It deletes all the containers along with volumes created.
