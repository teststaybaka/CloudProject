var SERVICE_TAGS = ['Nails', 'Tutoring', 'Childcare', 'Fashion', 'Beauty', 'Housing', 
                    'Housekeeping', 'Designated driving', 'Cleaning', 'Repair and Maintainance',
                    'Construction', 'Education', 'Entertainment', 'Personal Grooming', 'Public Utility',
                    'Risk Management', 'Social Services', 'Transport'
 ]

$(document).ready(function() {
    $("#service_tags").autocomplete({
             minLength: 0,
             source: function( request, response ) {
                 response( $.ui.autocomplete.filter(
                     SERVICE_TAGS, extractLast( request.term ) ) );
             },
             focus: function() {
                 return false;
             },
            select: function( event, ui ) {
                var terms = split( this.value );
                terms.pop();
                terms.push( ui.item.value );
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
        });
    $('.add-service-form').submit(function(evt) {
        evt.preventDefault();
        $.ajax({
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'JSON',
            url: window.location.href+"/post",
            success: function(res) {
                if (res.error) {
                    console.log(res.message);
                } else {
                    window.location.replace('/');
                }
            }
        });
    });
});
function split( val ) {
      return val.split( /,\s*/ );
    }
    function extractLast( term ) {
      return split( term ).pop();
    }