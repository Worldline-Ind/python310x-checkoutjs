$(document).ready(function() {
	if($("#siDetailsAtMerchantEndCond").val()=="true"){
					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="accNo">Account No</label></td>\
						<td><input type="text"  id="accNo" name="accNo"/> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="accountType">Account Type</label></td>\
						<td><select id="accountType" name="accountType" style="width:100%" ><option value="Saving">Saving</option>\
									<option value="Current">Current</option> \
						</select></td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="accountHolderName">Account Name</label></td>\
						<td><input type="text"  id="accountHolderName" name="accountHolderName" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="aadharNo">Aadhar No</label></td>\
						<td><input type="text"  id="aadharNo" name="aadharNo" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="ifscCode">IFSC Code</label></td>\
						<td><input type="text"  id="ifscCode" name="ifscCode" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="debitStartDate">Debit Start Date</label></td>\
						<td><input type="date" id="debitStartDate" name="debitStartDate" style="width:98%" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="debitEndDate">Debit End Date</label></td>\
						<td><input type="date" id="debitEndDate" name="debitEndDate" style="width:98%" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="maxAmount">Max Amount</label></td>\
						<td><input type="text"  id="maxAmount" name="maxAmount" /> </td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="amountType">Amount Type</label></td>\
						<td><select id="amountType" name="amountType" style="width:100%" ><option value="M">Variable</option>\
									<option value="F">Fixed</option> \
						</select></td></tr>');

					$("#worldline_merchant_table").append('<tr > \
						<td scope="row"><label for="frequency">Frequency</label></td>\
						<td><select id="frequency" name="frequency" style="width:100%"><option value="ADHO">As and when presented</option>\
									<option value="DAIL">Daily</option> \
									<option value="WEEK">Weekly</option> \
									<option value="MNTH">Monthly</option> \
									<option value="QURT">Quarterly</option> \
									<option value="MIAN">Semi Annually</option> \
									<option value="YEAR">Yearly</option> \
									<option value="BIMN">Bi-monthly</option> \
						</select></td></tr>');

	} else {
		$('<input>').attr({ type: 'hidden', id: 'accNo', name: 'accNo'}).appendTo('form');
		$('<input>').attr({ type: 'hidden', id: 'debitStartDate', name: 'debitStartDate'}).appendTo('form');
		$('<input>').attr({ type: 'hidden', id: 'debitEndDate', name: 'debitEndDate'}).appendTo('form');
		$('<input>').attr({ type: 'hidden', id: 'maxAmount', name: 'maxAmount'}).appendTo('form');
		$('<input>').attr({ type: 'hidden', id: 'amountType', name: 'amountType'}).appendTo('form');
		$('<input>').attr({ type: 'hidden', id: 'frequency', name: 'frequency'}).appendTo('form');
	}
	function handleResponse(res) {
			if (typeof res != 'undefined' && typeof res.paymentMethod != 'undefined' && 
				typeof res.paymentMethod.paymentTransaction != 'undefined' && 
				typeof res.paymentMethod.paymentTransaction.statusCode != 'undefined' && res.paymentMethod.paymentTransaction.statusCode == '0300') {
						// success block
			} else if (typeof res != 'undefined' && typeof res.paymentMethod != 'undefined' && 
				typeof res.paymentMethod.paymentTransaction != 'undefined' && 
				typeof res.paymentMethod.paymentTransaction.statusCode != 'undefined' && res.paymentMethod.paymentTransaction.statusCode == '0398') {
							// initiated block
			} else {
					// error block
			}   
		};

	$(document).off('click', '#submit').on('click', '#submit', function(e){
		e.preventDefault();
		var str = $("#form").serialize();
		$.ajax({
		type: 'POST',
		cache: false,
		data: str,
		url: "/payment",
		success: function (response)
			{	
				var configJson = response;
				console.log(configJson);
				configJson.consumerData.responseHandler = handleResponse;
				$.pnCheckout(configJson);
				if(configJson.features.enableNewWindowFlow){
					pnCheckoutShared.openNewWindow();
				}

			},
		error: function (response)
			{
				alert(str);
			}
		});
	});
});
