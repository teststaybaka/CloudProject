$(document).ready(function(){
	$("#facebook-login").click(function(){
		FB.getLoginStatus(function(response){
			if(response.status === "connected"){
				$.post("/signin", {"fb-access-token":response.authResponse.accessToken},function(){
					window.location.replace("/");
				});
			} 
			else{
				FB.login(function(response) {
  				if (response.status === 'connected')
  					sendConnectedResponse(response);
				}, {scope: 'email'});
			}
		});
	});

	$("#signup").submit(function(){
			$.post('/signin', $(this).serialize(), function (){
	            window.location.replace("/");
	    	});
    	}
    );

    $("#signin").submit(function(){
			$.post('/signin', $(this).serialize(), function (){
	            window.location.replace("/");
	    	});
    	}
    );
});


function sendConnectedResponse(callback){
	var auth_id, firstname, lastname, gender, email;
	FB.api('/me', {fields: 'first_name, last_name, gender, email'}, function(response){

		auth_id = response.id;
		firstname = response.first_name;
		lastname = response.last_name;
		gender = response.gender;
		email = response.email;

		$.post("/signin", 
			{
				"fb-access-token":callback.authResponse.accessToken,
				"auth_id":auth_id,
				"firstname":firstname,
				"lastname":lastname,
				"gender":gender,
				"email":email
			},
			function(data){
				window.location.replace("/");
			}
		);
	});
}
  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
  }