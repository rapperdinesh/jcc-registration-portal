from __future__ import unicode_literals
from django.shortcuts import render
from .models import Team
from .forms import RegistrationForm
from . import sms_service


def index(request):

    is_team_name_taken = False

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            team_name = request.POST['team_name']
            player_one_contact = request.POST['player_one_contact']
            player_two_contact = request.POST['player_two_contact']
            player_one_email = request.POST['player_one_email']
            player_two_email = request.POST['player_two_email']

            team = Team.objects.filter(
                player_one_email=player_one_email, player_two_email=player_two_email).first()

            if not team:
                unique_team_id = sms_service.generate(
                    team_name + player_one_contact + player_two_contact)
                new_team = Team(
                    team_name=request.POST['team_name'],
                    player_one_name=request.POST['player_one_name'],
                    player_one_email=request.POST['player_one_email'],
                    player_one_contact=request.POST['player_one_contact'],
                    player_one_hall=request.POST['player_one_hall'],
                    player_two_name=request.POST['player_two_name'],
                    player_two_email=request.POST['player_two_email'],
                    player_two_contact=request.POST['player_two_contact'],
                    player_two_hall=request.POST['player_two_hall'],
                    unique_team_id=unique_team_id
                )
                new_team.save()

                sms_service.send_message(
                    team_name, unique_team_id, player_one_contact)
                sms_service.send_message(
                    team_name, unique_team_id, player_two_contact)
                 
                ####To send confirmation email####

                #subject = 'Successfull Registration '
                #message = 'You have succesfully registered for JUNIOR CODECRACKER!!! BEST OF LUCK !!!'
                #from_email = settings.DEFAULT_FROM_EMAIL
                #to_list = ['player_one_email', 'player_two_email', settings.DEFAULT_FROM_EMAIL]
                connection = mail.get_connection()

                # Manually open the connection
                connection.open()

                # Construct an email message that uses the connection
                email1 = mail.EmailMessage(
                    'Successfull Registration in JCC',
                    'Congratulations, You have succesfully registered for JUNIOR CODECRACKER!!! BEST OF LUCK',
                    settings.DEFAULT_FROM_EMAIL,
                    [player_one_email],
                    connection=connection,
                )
                email1.send() # Send the email

                # Construct two more messages
                email2 = mail.EmailMessage(
                    'Successfull Registration in JCC',
                    'Congratulations, You have succesfully registered for JUNIOR CODECRACKER!!! BEST OF LUCK',
                    settings.DEFAULT_FROM_EMAIL,
                    [player_two_email],
                )

                # Send the two emails in a single call -
                connection.send_messages([email2])
                # The connection was already open so send_messages() doesn't close it.
                # We need to manually close the connection.
                connection.close()

                #### EMAIL PART ENDS HERE ####
                
                return render(request, 'success.html', {'unique_team_id': unique_team_id})

            else:
                is_team_name_taken = True
    else:
        form = RegistrationForm()

    context = {'form': form, 'is_team_name_taken': is_team_name_taken}
    return render(request, 'register.html', context)
