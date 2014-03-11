from nose.plugins import Plugin
from nose.result import TextTestResult
import nose.core
import gc
import resource


class MemoryTestResult(TextTestResult):

    def startTest(self, test):
        super(MemoryTestResult, self).startTest(test)
        gc.collect()
        self.mem_before = self.using()

    def stopTest(self, test):
        gc.collect()
        self.mem_after = self.using()
        if not self.wasSuccessful():
            pct = 100 * float(self.mem_after) / float(self.mem_before)
            msg = '''
Memory usage too high:
    Start:      %s mb
    End:        %s mb
---------------------------
    Increase:   %s%%''' % (
                self.mem_before / (1024 * 1024),
                self.mem_after / (1024 * 1024),
                '{0:.3g}'.format(pct - 100)
            )
            self.addFailure(
                test,
                (Exception, Exception(msg), None)
            )
        else:
            self._addSuccess(test)

        super(MemoryTestResult, self).stopTest(test)

    def wasSuccessful(self):
        if self.mem_after > self.mem_before * 1.1:
            return False
        return True

    def addSuccess(self, test):
        pass

    def _addSuccess(self, test):
        msg = 'ok - %s' % self._get_format_string()
        self.stream.writeln(msg)
        self.stream.flush()

    def addFailure(self, test, err):
        super(MemoryTestResult, self).addFailure(test, err)
        msg = '%s' % self._get_format_string()
        self.stream.writeln(msg)
        self.stream.flush()

    def _get_format_string(self):
        pct = 100 * float(self.mem_after) / float(self.mem_before)
        before = self.mem_before / (1024 * 1024)
        after = self.mem_after / (1024 * 1024)
        return '%smb/%smb (%s%%)' % (before, after, '{0:.3g}'.format(pct - 100))

    def using(self):
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage[2] * resource.getpagesize()


class NoseTestSuiteRunner(nose.core.TextTestRunner):

    def _makeResult(self):
        return MemoryTestResult(
            self.stream,
            self.descriptions,
            self.verbosity,
            self.config
        )


class MemoryGrindPlugin(Plugin):
    """A nose plugin which has watches test case memory usage"""
    name = 'nose-memory-grind'

    def prepareTestRunner(self, runner):
        return NoseTestSuiteRunner(
            runner.stream,
            verbosity=self.conf.verbosity,
            config=self.conf
        )
