$(document).ready(function ()
{
    $('.dateRangePicker')
            .datepicker({
                format: 'mm/dd/yyyy',
                startDate: '01/01/2015',
                endDate: '12/31/2015'
            })
            .on('changeDate', function (e) {
                // Revalidate the date field
                $('.dateRangeForm').bootstrapValidator('updateStatus', 'date', 'NOT_VALIDATED').bootstrapValidator('validateField', 'date');
            })
            .change(function () {
                validate();
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
                        min: '01/01/2015',
                        max: '12/31/2015',
                        message: 'Invalid date'
                    }
                }
            }
        }
    });

    function validate()
    {
        var start_date = $('#startDate').val();
        var end_date   = $('#endDate').val();

        if (start_date.trim().length !== 0 && end_date.trim().length !== 0)
        {
            if (start_date <= end_date)
            {
                $('#alert').text('');
                $('#loadData').attr('disabled', false);
            } else
            {
                $('#alert').text('Invalid date range.');
            }

        } else
        {
            $('#loadData').attr('disabled', true);
        }
    }
});

