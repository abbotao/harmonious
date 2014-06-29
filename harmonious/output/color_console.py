from harmonious.decorators import Before, After
from harmonious.output.results import analyze_results

class bgcolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD_BLACK = '\033[1;30m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_MAGENTA = '\033[1;35m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    UNDERSC = '\033[4m'
    OFF = '\033[0m'

@Before.Output.all
def output_runner():
    print bgcolor.BOLD + "Running Test Plans" + bgcolor.OFF

@Before.Output.testplan
def output_testplan_name(test_plan):
    print bgcolor.BOLD + "Test Plan:" + bgcolor.OFF + bgcolor.BLUE + " %s" % test_plan.name + bgcolor.OFF

@Before.Output.task
def output_task_name(task):
    print bgcolor.BOLD + "\tTest Case:" + bgcolor.OFF + bgcolor.BLUE + " %s" % task.name + bgcolor.OFF

@Before.Output.step
def output_step_name(step):
    print bgcolor.BLUE + "\t- %s" % step.name + bgcolor.OFF

@After.Output.directive
def output_directive_status(directive, result):
    if result.exception is not None:
        print bgcolor.RED,
    else:
        print bgcolor.GREEN,
    print "\t\t-",
    print directive.string,
    if result.exception is not None:
        print " ... FAIL" + bgcolor.OFF
    else:
        print bgcolor.OFF

@After.Output.all
def output_summary(results):
    summary = analyze_results(results)

    print bgcolor.BOLD + "Results:" + bgcolor.OFF
    print bgcolor.BOLD + "Test plans run: " + bgcolor.OFF + str(summary.plan_count) + bgcolor.BOLD + " Test plans in error: "  + bgcolor.OFF + str(summary.in_error)
    print bgcolor.BOLD + "Errors:" + bgcolor.OFF
    for error in summary.errors:
        print bgcolor.RED + error[0] + bgcolor.OFF
        for item in error[1]:
            if type(item) == tuple:
                print "\t-" + item[0]
                print "\t\tError: " + item[1]
            else:
                print "\t-" + item