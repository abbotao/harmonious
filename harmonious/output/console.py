from harmonious.decorators import Before, After
from harmonious.output.results import analyze_results

@Before.Output.all
def output_runner():
    print "Running Test Plans"

@Before.Output.testplan
def output_testplan_name(test_plan):
    print "Test Plan: %s" % test_plan.name

@Before.Output.task
def output_task_name(task):
    print "\tTest Case: %s" % task.name

@Before.Output.step
def output_step_name(step):
    print "\t* %s" % step.name

@After.Output.directive
def output_directive_status(directive, result):
    print "\t\t-",
    print directive.string,
    if result.exception is not None:
        print " ... FAIL"
    else:
        print ""

@After.Output.all
def output_summary(results):
    summary = analyze_results(results)

    print "Results:"
    print "Test plans run: %s, Test plans in error: %s" % (summary.plan_count, summary.in_error)
    print "Errors:"
    for error in summary.errors:
        print error[0]
        for item in error[1]:
            print "\t",
            if type(item) == tuple:
                print "%s - %s" % item
            else:
                print item