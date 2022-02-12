import handler

event = {'dry_run': 1, 'regions': ['eu-west-1']}
handler.lambda_handler(event, None)
