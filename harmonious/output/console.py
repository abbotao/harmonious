from harmonious.decorators import Before, After

@Before.Output.all
def output_runner():
    print "Running Test Plans"

@Before.Output.testplan
def output_testplan_name(testplan):
    print "Test Plan: %s" % testplan.name

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