// http://formvalidation.io/examples/bootstrap-datepicker/
// http://formvalidation.io/getting-started/

$(document).ready(function() 
{
	//$('.dateRangePicker').datepicker({ dateFormat: 'mm/dd/yyyy'}).datepicker("setDate", new Date());
	
	/*var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();

	if (dd < 10) 
		dd='0'+dd

	if (mm < 10) 
		mm='0'+mm

	today = mm+'/'+dd+'/'+yyyy;*/

    $('.dateRangePicker')
        .datepicker({
            format: 'mm/dd/yyyy',
            startDate: '01/01/2015', //'01/01/2010',
            endDate: '12/31/2015', //today
        })
        .on('changeDate', function(e) {
            // Revalidate the date field
            $('.dateRangeForm').bootstrapValidator('updateStatus', 'date', 'NOT_VALIDATED')
            .bootstrapValidator('validateField', 'date');
        });

    $('.dateRangeForm').bootstrapValidator({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            date: {
                validators: {
                    notEmpty: {
                        message: 'Required field'
                    },
                    date: {
                        format: 'MM/DD/YYYY',
                        min: '01/01/2015', //'01/01/2010',
                        max: '12/31/2015', //today,
                        message: 'Invalid date'
                    }
                }
            }
        }
    });
});