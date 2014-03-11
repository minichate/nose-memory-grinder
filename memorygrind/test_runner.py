from __future__ import division
from nose.plugins import Plugin
from nose.result import TextTestResult
import nose.core
import gc
import resource

MEMORY_USAGE_MESSAGE = '''Memory usage too high:
    Start:      %s
    End:        %s
---------------------------
    Increase:   %s%%'''


class MemoryTestResult(TextTestResult):

    def startTest(self, test):
        super(MemoryTestResult, self).startTest(test)
        gc.collect()
        self.mem_before = self.using()

    def stopTest(self, test):
        self.mem_after = self.using()
        if not self.wasSuccessful():
            pct = 100 * float(self.mem_after) / float(self.mem_before)
            msg = MEMORY_USAGE_MESSAGE % (
                self.humanize_bytes(self.mem_before),
                self.humanize_bytes(self.mem_after),
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
        if self.mem_after > self.mem_before * 1.05:
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
        before = self.mem_before
        after = self.mem_after
        return '%s/%s (%s%%)' % (
            self.humanize_bytes(before),
            self.humanize_bytes(after),
            '{0:.3g}'.format(pct - 100)
        )

    def humanize_bytes(self, bytes, precision=1):
        abbrevs = (
            (1<<50L, 'PB'),
            (1<<40L, 'TB'),
            (1<<30L, 'GB'),
            (1<<20L, 'MB'),
            (1<<10L, 'kB'),
            (1, 'bytes')
        )
        if bytes == 1:
            return '1 byte'
        for factor, suffix in abbrevs:
            if bytes >= factor:
                break
        return '%.*f %s' % (precision, bytes / factor, suffix)

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
