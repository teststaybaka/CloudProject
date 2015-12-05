$(document).ready(function(){
		$("#facebook-login").click(function(){
			if(checkLoginState() === "connected")
				return;
			FB.login(function(response) {
  				if (response.status === 'connected') {
    			// Logged into your app and Facebook.

    			$.post("https://"+window.location.hostname+"/signin", 
    				JSON.stringify({"fb-access-token":response.accessToken}),
    				function(data){

    				}
    			)
    			//failure
    			window.location.replace("https://"+window.location.hostname+"/signup");
			  } else if (response.status === 'not_authorized') {
			    // The person is logged into Facebook, but not your app.
			    window.location.replace("https://"+window.location.hostname+"/signin");
			  } else {
    			// The person is not logged into Facebook, so we're not sure if
    			// they are logged into this app or not.
    			window.location.replace("https://"+window.location.hostname+"/signin");
  			}
			});
		})

});

  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);

    window.location.replace("https://"+window.location.hostname+"/signin");
  }

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
  	var status = 'unknown';
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
      status = response.status;
    });
    return status;
  }

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
    });
  }