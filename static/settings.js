$(document).ready(function() {
    $('.change-settings-form').submit(function() {
        $.ajax({
            type: 'POST',
            data: $(this).serialize(),
            success: function(result) {
                if (result.error) {
                    console.log(result.message);
                } else {
                    window.location.replace('/');
                }
            }
        })
    });
});