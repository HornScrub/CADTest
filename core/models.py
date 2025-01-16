from django.db import models

'''
README:
    Everything in the " ''' ''' " block comments are notes, probably things we want to fix. The "#" block comments are descriptions. I'm putting
    notes above particular segments I know there is an issue, and I'm putting general fixes up on top. Theres not a good order to the notes yet,
    its a bit stream of conciousness. 

'''


'''
For API questions, I have to explore the best way to store and serve this info. Right now, I'm deciding between creating views to serve
info thats API appropriate, like turning TextFields into JSON through a view, or if it would just be better to store the info as JSON to 
make the views (and thus the endpoints) a lot easier to write. I'm opting for the former, makes the data more flexible? I think?

For missing data, we have to deside if we should store it use null or placeholder values. I don't know the impacts of either. I imagine null might
be better, but then I'd have to figure out what happens when we serve NULL to a caller, make sure they are ready for it. Or, we could just
account for it when we are creating the view (if NULL, first_name = "", etc.)

Need to read what "related_name" fields of the ManyToManyRelationships mean, I think I'm not describing them correctly here.

A ton of stuff needs input validation or sanitization. I imagine sanitization is the best route here when we are dealing with the real time back
end system like Lambda, but it could lead to some funky data that we would need to account for. I think we can sanatize through the 
save() function of models, but I'm not sure if that's the best way to do it. Eventually we should also be doing input validation on the 
front end.

I would love to see some SOP documentation on how LEOs and dispatchers interact, it would give us a good idea of what kind of information is
important. I imagine we could get that from a police department?

For backend right now, I'm starting with what Lambda will be hitting to show of the MVP.

    # Vehicles - Should cover all the physical, legal, and criminal aspects of a vehicle, like license plates, VINs, ownership. These can point 
        to People as owners or who have been related to the car (took their info at a traffic stop as a passenger, was a witness to a hit and run,
        etc.)
        Vehicles should also point to incidents they were involved in, whether they be traffic or criminal.
    # Addresses
    # Persons
    # Incidents
    # Warrents
    # 
    # Maybe more?

I'll want to look into Fire and EMS eventually, but I'm sticking to police stuff for now.


Eventually, I'll have to figure out authentication and authorization as we make a front end, and Django should have some systems for that. 
That would look like a User() model, that has Dispatchers() and LEO()s and stuff. Django has some tools for that I have to learn.

# Vehicle, needs VIN, descripton, augments maybe (spoilers, lights, decals), probably more?
'''
class Vehicle(models.Model):
    # license_plate: Should make this a foreign key, and embed a function to check license plate validity (per state? county?)
    license_plate = models.CharField(max_length=10, unique=True) 
    # owner_name: 
    owner_name = models.models.ForeignKey('Person', on_delete=models.CASCADE, related_name='vehicles')
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='vehicles')  # Nullable if no address
    # vehicle_make, vehicle_model : Should standardize inputs (probably all inputs) using save() function eg. input- "Ford " " Focus" -> "FORD" "FOCUS"
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    # is_stolen : Should point to a member of an Incident() maybe?
    is_stolen = models.BooleanField(default=False)
    # outstanding warrents: This probably should point to the owner's warrents:
    outstanding_warrants = models.TextField(blank=True, null=True)

    # Use save() to standardize the input before we create the object. We could add more members here besides make and model

    def save(self, *args, **kwargs):
        # Standardize fields
        self.vehicle_make = self.vehicle_make.strip().upper()
        self.vehicle_model = self.vehicle_model.strip().upper()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.license_plate

'''
# Address, should be owned by Persons, Vehicles, Incidents. Maybe modify this to have descriptions of locations if its incomplete
#   (like "Red house next to Eastwood Park", "10 miles before Exit 28", "Southbound I-5 by Pebble Beach", something like that, or
#   maybe that should be its own model), or maybe point to nearest valid address
'''
class Address(models.Model):
    street = models.CharField(max_length=255, blank=True, null=True)  # e.g., "123 Elm St"
    apartment = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Apt 4B"
    city = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Austin"
    state = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Texas"
    country = models.CharField(max_length=50, default="USA")  # Default to USA
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # e.g., ZIP or international postal code
    owner = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='addresses') 
    residents = models.ManyToManyField('Person', related_name='residences', blank=True)

    # Use save() to standardize the input before we add the object to db
    def save(self, *args, **kwargs):
        # Standardize text fields
        if self.street:
            self.street = self.street.strip().upper()
        if self.apartment:
            self.apartment = self.apartment.strip().upper()
        if self.city:
            self.city = self.city.strip().upper()
        if self.state:
            self.state = self.state.strip().upper()
        if self.postal_code:
            self.postal_code = self.postal_code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        address = f"{self.street or 'UNKNOWN'}"
        if self.apartment:
            address += f", {self.apartment}"
        address += f", {self.city or 'UNKNOWN'}, {self.state or 'UNKNOWN'}, {self.country}, {self.postal_code or 'UNKNOWN'}"
        return address

'''
For Person's, I have to decide if I should be saving LEO, Dispatcher info via this class or keep it seperate, makes sense to keep it seperate if
we aren't concerned with the officer's personal info and the DB is just going to have suspect info, keep the login info for LEOs and Dispatchers 
in a whole seperate class with just some really basic personal info and login stuff, don't need to keep their PII alongside everyone else.

I could subclass Suspect here and only introduce criminality fields there, keep this parent class criminal agnostic

For Person's personal info supported by documentation, we should figure out if primary members flows downstream from that supporting documentation,
and if so if we even need those data members like first_name, address. 

I don't know what the lifecycle of our DB looks like yet; are we generating our DB from reading a DB of drivers licenses, passports, police DB, 
a mix of them? Something else? Once we get this far I'll definitely need to research this. My question is, for something like a VIN for a Vehicle
or a name of a Person, should our app be getting that information from the supporting documentation (like drivers licenses, birth certificattes, passports,
whatever) or should we be storing that info manually in our DB? Its a weird question, probably will come back up later in the project.

Is the DB tabula rasa, info only created by callers? I imagine not, what good is a plate check if we don't even know what plates are out there? 

In the event we are reading from another support DB a Person's info, I can imagine pulling from that DB and storing it locally
can cause clashes if that primary DB is updated with correct info. In that event, we should only ever be pulling from that DB if possible. On the other hand,
that sounds really expensive and probably isn't possible, but I have no conception of how databases interact with each other. I really have no clue what happens there.\

'''


class Person(models.Model):
    
    # Identification
    first_name = models.CharField(max_length=40)
    middle_name = models.CharField(max_length=40, blank=True, null=True)  # could be null for individuals without middle names
    last_name = models.CharField(max_length=40)
    full_name = first_name + " " + middle_name + " " + last_name
    aliases = models.TextField(blank=True, null=True)  # Comma-separated or JSON list

    # Identification Numbers
    nationality = models.CharField(max_length=50, blank=True, null=True)

    '''
    drivers_license - this should be its own model, person's can have multiple licenses, info on license will contradict stated personal info, etc.
    All these members are just placeholders, need to be elaborated. Might be more members that just this.
    '''

    drivers_license_number = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='drivers_license_address') # Address stated on DL
    drivers_license_first_name = models.CharField(max_length=40, blank=True, null=True)
    drivers_license_middle_name = models.CharField(max_length=40, blank=True, null=True)
    drivers_license_last_name = models.CharField(max_length=40, blank=True, null=True)
    drivers_license_sex = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_gender = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_height = models.IntegerField(blank=True, null=True)
    drivers_license_weight = models.IntegerField(blank=True, null=True)
    drivers_license_eye_color = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_state_issued = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_issue_date = models.CharField(max_length=20, blank=True, null=True) # Issue date of DL
    drivers_license_expiry_date = models.DateField(blank=True, null=True) # Expiration date of DL
    drivers_license_discriminator = models.CharField(max_length=20, blank=True, null=True) # Unique number that identifes driver's license from other documents
    drivers_license_class = models.CharField(max_length=20, blank=True, null=True)
    drivers_license_end = models.DateField(blank=True, null=True) # Driver's license endorsements
    drivers_license_rstr = models.CharField(max_length=20, blank=True, null=True) # Driver's license restrictions
    drivers_license_donor = models.CharField(max_length=20, blank=True, null=True) # Organ donor status

    '''
    passport, nationality - need to do research on info contained on a US passport, will need to be expanded. Probably needs to be its own model
    as well. Will we have to create a model per nation, they all have their own rules.
    '''

    passport_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()

    # Contact Information

    '''
    email - need to standardize in uppercasing 
    '''

    email_primary = models.EmailField(unique=True)
    email_secondary = models.EmailField(blank=True, null=True)
    
    '''
    Phone_number_primary, type - need to standardize in the (x) (xxx) xxx-xxxx format and uppercasing
    '''
    phone_number_primary = models.CharField(max_length=15, blank=True, null=True)
    phone_number_primary_type = models.CharField(max_length=20, blank=True, null=True) # e.g., "Mobile", "Home", "Work"

    '''
    home_address - we should account for in the event of a non-traditional residential address (homeless, mobile home), either updating 
    Address or doing something else.
    '''

    home_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='residents')
    work_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='employees')

    # Physical Description
    gender = models.CharField(max_length=20, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    '''
    Height, weight - should decide between imperial vs metric, leaning imperial, maybe should be TextField for appended lbs/feet, inches
    '''
    height = models.IntegerField(blank=True, null=True)  # in cm
    weight = models.IntegerField(blank=True, null=True)  # in kg
    eye_color = models.CharField(max_length=20, blank=True, null=True)
    '''
    distinguishing_marks - catch all for tattoos, piercings, scars, burns, augmentations, etc., might need to be expanded 
    '''
    has_distinguishing_marks = models.BooleanField(default=False)
    distinguishing_marks = models.TextField(blank=True, null=True)

    # Personal Information
    occupation = models.CharField(max_length=100, blank=True, null=True)
    employer = models.CharField(max_length=100, blank=True, null=True)

    '''
    employer_person - could be supervisor, could expand to coworkers, subordinates, etc.
    '''
    employer_person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, related_name='employer_person')
    employer_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='employer_address')

    '''
    vehicles_owned - should be vehicles currently owned in their name, should make something for past vehicles owned
    '''

    vehicles_owned = models.ManyToManyField('Vehicle', related_name='owners', blank=True)

    # Medical Information

    '''
    is_5150 - should describe someone gravely disabled through mental illness, not sure the right term for this
    '''
    is_5150 = models.BooleanField(default=False)
    '''
    medical_conditions - catch-all for any medical conditions from allergy to visable disability, probably should be expanded to seperate the two
    '''

    medical_conditions = models.TextField(blank=True, null=True)
    '''
    mental_health_history - catch-all for any mental health history, ambigious right now if this could point to LEO incidents or caller provided info, etc.
    '''
    mental_health_history = models.TextField(blank=True, null=True)
    
    '''
    Associations - I think its important to have reports of associations for LEO investigation, but I'm not sure if I should have explicit relationships here
    or relationships through incidents, etc. Makes sense for me right now to make the relationships explicit
    Associations could be anything to family, friends, roomates, coworkers, crime partners, addresses, vehicles, incidents, etc. Needs to be
    expanded'''
    
    #Associations

    ## Familial Relationships
    family_of = models.ManyToManyField('Person', related_name='family', blank=True) # Should catch cousins, aunts/uncles, or maybe its redundant
    spouse_of = models.ManyToManyField('Person', related_name='spouses', blank=True)
    parent_of = models.ManyToManyField('Person', related_name='children', blank=True)
    sibling_of = models.ManyToManyField('Person', related_name='siblings', blank=True)
    child_of = models.ManyToManyField('Person', related_name='parents', blank=True)
    grandparent_of = models.ManyToManyField('Person', related_name='grandchildren', blank=True)
    grandchild_of = models.ManyToManyField('Person', related_name='grandparents', blank=True)

    ## Social Relationships
    friends_with = models.ManyToManyField('Person', related_name='friends', blank=True)
    roommates_with = models.ManyToManyField('Person', related_name='roommates', blank=True)
    coworkers_with = models.ManyToManyField('Person', related_name='coworkers', blank=True)
    acquaintances_with = models.ManyToManyField('Person', related_name='acquaintances', blank=True)
    '''
    group_member_of - Might want to include their social groups and functions, agnostic to criminality for now (could be criminal gang or benign club)
    '''
    group_member_of = models.ManyToManyField('TextField', related_name='groups', blank=True)

    ## General Associations
    phone_number_associated = models.CharField(max_length=15, blank=True, null=True)
    addresses_associated = models.ManyToManyField('Address', related_name='owners', blank=True)
    vehicles_associated = models.ManyToManyField('Vehicle', related_name='associated_vehicles', blank=True)
    persons_associated = models.ManyToManyField('Persons', related_name='associated_persons', blank=True)

    '''
    incidents_associated - I'd want this to represent incidents they aren't the primary subject of, eg. made the emergency call,
    gave testimony, that sort of thing
    '''
    incidents_associated = models.ManyToManyField('Incident', related_name='incidents_associated', blank=True)



    # Criminality

    has_active_warrants = models.BooleanField(default=False)
    active_warrants = models.TextField(blank=True, null=True)
    warrant_history = models.TextField(blank=True, null=True)

    on_probation = models.BooleanField(default=False)
    parole_officer = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, related_name='parolees')

    has_criminal_history = models.BooleanField(default=False, null=True)
    criminal_history_primary = models.TextField(blank=True, null=True)

'''
    A lot of the way I'm approaching this project is my superficial understanding of how dispatch work from firsthand experience (report to dispatch):
    
    (I used to do Asset Protection and I was calling 911 a lot. The dispatcher would always be asking the same kinds of things, so I kinda figured out exactly what to say to minimize get
    the information dispatch wanted in as lightweight a way as possible. For example, the conversation would go something like this:
    - "911, what's your emergency?"
    - "Hello, I'm calling from Nordstrom Asset Protection at the Irvine Spectrum. We currently have detained an individual for shoplifting, he is 
    located in the Asset Protection office on the first floor of the building. He is restrained and cooperative.
        (So what I sussed out over a lot of calls is that the dispatcher really wants to ASAP the location (Irvine Spectrum) and intensity of the situation, like if we are
        grappling with the dude and its a big fight, or if the situation is basically over and we are just waiting for the cops to show up. I also found
        they really don't need the address for something like "Nordstrom at the Irvine Spectrum", they either know right away the address for the Spectrum
        since there are so many calls there, or they can look it up really fast without asking me).
    
    - "When did this happen?"
    - "About 5 minutes ago."
    - "What's the name of the individual?"
    - "It says on his license his name is John Doe"
        (I'm not sure if they really care whether thats the real name or not, but I'd always say I have the license in front of me, to support the info.
        The responding officer validates the license when they arrive anyway, so I'm not sure its too important. I think they just want a name to call the suspect,
        because sometimes the cops arrive even after I've given info to dispatch and they are supprised to learn the person's on parole or something.)
    - "Any weapons present?"
    - "We removed a pocket knife from him, its in the office."
    - "What's his date of birth?"
    - "January 1st, 2000"
    - "What's his address?"
    - "123 Main St, Irvine, CA 92612"

    I think at this point they ask for my info as a contact, just my name and phone number. And they let me know they sent someone out. However long later,
    could be 10 to 60 minutes later, PD would arrive, conduct their investigation on the subject as they do license check to dispatch using 10 codes and military phonetics [sometimes
    subject wouldn't have a license, they would just provide their name, birthdate, home address], and PD would relay that to dispatch, who I guess would say whether that info was accurate
    or not. If they couldn't ID the subject, they would have to take them back to the station to fingerprint them. Usually, if they could ID the subject, they would "arrest" them 
    [to me arrest always implied taking them back to the station], write a ticket and release them. Priors or extenuating circumstances they might book them.
    For me, the 2nd would usually take my license and info to record me as the arresting indivudual, I'd give them basic info like when the subject arrived to the store, when I established intent, 
    when they arrived and I attempted the arrest [there were a lot of dotting i's and crossing t's I think for them to responsibly make an arrest, as well as for Asset Protection people to
    responsibly detain people without putting the company in legal jeapordy.] I'd fill out some Irvine PD Public Person's Arrest form stating I was the guy who arrested them. Sometimes PD
    would just listen, sometimes they would take notes. Once the subjects released, they might debrief with us or head out, where I assume they write a report in their vehicles.)
    
    I'm also only familiar with dispatch when it comes to a firefighter friend and an EMS friend I interogatted about their interactions with dispatch

    As the tool right now we are making is for non-emergency PD calls, I really want a source of how that works and what SOP are, what kind of info they need,
    etc. I could lean on our team, but I'd also see if there was some resource I could look at.
    '''