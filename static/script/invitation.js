var invitation = document.querySelectorAll(".invitation");

invitation.forEach(invitation => { 
  var redButton = invitation.querySelector(".dialog-box__red-button");
    console.log(redButton);
    
    redButton.addEventListener('click', function (e) {
      invitation.remove();
      });
});
