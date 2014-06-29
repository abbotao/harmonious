from selenium.common.exceptions import NoSuchElementException

from harmonious.exceptions import ExpectedThrownError

from collections import namedtuple

Summary = namedtuple("Summary", ['plan_count', 'in_error', 'errors'])

def analyze_results(result):
    plan_count = 0
    error_plan = 0
    for test_plan in result:
        plan_count += 1
        if test_plan.exception is not None:
            error_plan += 1
            break
        else:
            for (case_name, test_case) in test_plan.iteritems():
                if test_case.exception is not None:
                    error_plan += 1
                    break
                else:
                    for (step_name, step) in test_case.iteritems():
                        if step.exception is not None:
                            error_plan += 1
                            break
                        else:
                            for (directive_str, directive) in step.iteritems():
                                if directive.exception is not None:
                                    error_plan += 1
                                    break

    errors = []
    for test_plan in result:
        if test_plan.exception is not None:
            errors.append(test_plan.name, translate_exception_to_reason(test_plan.exception))
        else:
            for (case_name, test_case) in test_plan.iteritems():
                if test_case.exception is not None:
                    errors.append(("%s - %s" % (test_plan.name, case_name), translate_exception_to_reason(test_case.exception)))
                else:
                    for (step_name, step) in test_case.iteritems():
                        if step.exception is not None:
                            errors.append(("%s - %s(%s)" % (test_plan.name, case_name, step_name), translate_exception_to_reason(step.exception)))
                        else:
                            location = "%s - %s(%s)" % (test_plan.name, case_name, step_name)
                            directives = []
                            in_error = False
                            for (directive_str, directive) in step.iteritems():
                                if directive.exception is not None:
                                    in_error = True
                                    directives.append((directive_str, translate_exception_to_reason(directive.exception)))
                            if in_error:
                                errors.append((location,directives))

    return Summary(plan_count=plan_count, in_error=error_plan, errors=errors)


def translate_exception_to_reason(ex):
    if type(ex) == NoSuchElementException:
        return "Element to check was not found. (%s)" % ex.msg

    if type(ex) == AssertionError:
        return "Expectation not met. (%s)" % str(ex)

    if type(ex) == ExpectedThrownError:
        return "Expected an error, but didn't receive one."

    return "Exception caught. (%s: %s)" % (type(ex), str(ex))