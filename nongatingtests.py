import unittest
import re
import os
from .testutils import system


class TunirNonGatingtests(unittest.TestCase):

    def test_bash(self):
        """Tests the bash version as the same of upstream"""
        out, err, eid = system('bash --version')
        out = out.decode('utf-8')
        self.assertIn("-redhat-linux-gnu", out, out)


class TunirNonGatingtestsCpio(unittest.TestCase):

    def setUp(self):
        """Recording the current working directory"""
        self.current_working_directory = os.getcwd()

    def test_cpio(self):
        """Tests to check basic cpio functions"""

        outdir = '/var/tmp/cpio/cpio_out'
        indir = '/var/tmp/cpio/cpio_in'
        passdir = '/var/tmp/cpio/cpio_pass'

        if os.path.exists('/var/tmp/cpio'):
            system('rm -rf /var/tmp/cpio')

        system('mkdir -p %s' % outdir)
        system('mkdir -p %s' % indir)
        system('mkdir -p %s' % passdir)

        # Basic copy out test
        out, err, eid = system('ls | cpio -o > %s/cpio.out' % outdir)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Basic copy in test
        os.chdir(indir)
        out, err, eid = system('cpio -i < %s/cpio.out' % outdir)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Basic pass through test
        os.chdir(indir)
        out, err, eid = system('find . | cpio -pd %s' % passdir)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Check that the working directories are the same
        out, err, eid = system('diff %s %s &>/dev/null' % (passdir, indir))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

    def tearDown(self):
        """Returning to present directory"""
        os.chdir(self.current_working_directory)


class TunirNonGatingtestDiffutills(unittest.TestCase):

    def setUp(self):
        """Checking if packages are there"""
        out, err, eid = system('cmp -v &>/dev/null')
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('diff -v &>/dev/null')
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

    def test_cmp(self):
        """ Test to check cmp functionality"""
        diffutillsa = '/var/tmp/diffutilsa'
        diffutillsb = '/var/tmp/diffutilsb'
        system('rm %s %s &>/dev/null' % (diffutillsa, diffutillsb))

        test_file = open(diffutillsa, 'w')
        test_file.write('This is some text to play with')
        test_file.close()

        test_file = open(diffutillsb, 'w')
        test_file.write('This is some test to play with')
        test_file.close()

        # Basic test for cmp
        out, err, eid = system('cmp %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn('byte 16, line 1', out, out+err)

        # Compares two files using -b
        out, err, eid = system('cmp -b %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn(' line 1 is 170 x 163 s', out, out+err)

        # Expect this to pass as the difference is at byte 16
        out, err, eid = system('cmp -i 16 %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Expect this to have a different output to earlier
        out, err, eid = system('cmp -i 15:16 %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn('byte 1, line 1', out, out+err)

        # Chek that -n work
        out, err, eid = system('cmp -n 15 %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Verbose output
        out, err, eid = system('cmp -l %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn('16 170 163', out, out+err)

        # Silent - exit status only, first scheck that there is no outpu
        out, err, eid = system('cmp -s %s %s| wc -m' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn('0\n', out, out+err)
        out, err, eid = system('cmp -i 16 -s %s %s' % (diffutillsa, diffutillsb))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

    def test_diff(self):
        """Test for diff command"""
        f1 = '/var/tmp/testf1.txt'
        f2 = '/var/tmp/testf2.txt'
        rand_str = 'Here lyeth  muche rychnesse  in lytell space.   -- John Heywood'

        temp_file = open(f1, 'w')
        temp_file.write(rand_str)
        temp_file.close()

        temp_file = open(f2, 'w')
        temp_file.write(rand_str)
        temp_file.close()

        # Baseline check to ensure diff sees the files are the same.
        out, err, eid = system('diff %s %s &>/dev/null' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Convert a <space> to <space><tab> in F2 then check that diff sees the change
        # eid is 1 because files are different
        temp_file = open(f2, 'w')
        temp_file.write(rand_str.replace(' ', ' \t'))
        temp_file.close()

        out, err, eid = system('diff %s %s &>/dev/null' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        # Convert the first space in $F1 to 4 spaces and check that -E and
        # --ignore-tab-expansion works and sees no difference between the
        # two files.
        temp_file = open(f1, 'w')
        temp_file.write('        '+rand_str)
        temp_file.close()

        temp_file = open(f2, 'w')
        temp_file.write('\t'+rand_str)
        temp_file.close()

        out, err, eid = system('diff -E %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('diff --ignore-tab-expansion %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # reduce the 4 spaces to 3 and check diff -E sees a difference
        temp_file = open(f1, 'w')
        temp_file.write('   '+rand_str)
        temp_file.close()

        out, err, eid = system('diff -E %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        # Check -b --ignore-space-change add some spaces to the end of the line
        # to make sure.
        temp_file = open(f1, 'w')
        temp_file.write(rand_str + ' ')
        temp_file.close()

        temp_file = open(f2, 'w')
        temp_file.write(rand_str)
        temp_file.close()

        out, err, eid = system('diff -b %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('diff --ignore-space-change %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # The -b option ignotes difference in whitespace where it already exists.
        # Check that whitespace added in $F1 where non exists in $F2 is caught by
        # -b
        temp_file = open(f1, 'w')
        temp_file.write(rand_str.replace('ss', 's s'))
        temp_file.close()

        out, err, eid = system('diff -b %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        # Check -w --ignore-all-space
        out, err, eid = system('diff -w %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('diff --ignore-all-space %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Check -B --ignore blank lines, create some new files to work with first.
        temp_file = open(f1, 'w')
        temp_file.write(rand_str+'\n'+rand_str)
        temp_file.close()

        temp_file = open(f2, 'w')
        temp_file.write(rand_str+'\n'+''+'\n'+rand_str)
        temp_file.close()

        out, err, eid = system('diff %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        out, err, eid = system('diff -B %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(0, eid, out+err)

        out, err, eid = system('diff --ignore-blank-lines %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(0, eid, out+err)

        # Check -i --ignore-case, first ensure that diff sees a difference in case,
        # as we're using the files from the earlier test we need to use the -B option
        # too.
        temp_file = open(f1, 'r')
        replace_str = ''.join(temp_file.readlines()).replace('l', 'L')
        temp_file.close()
        temp_file = open(f1, 'w')
        temp_file.write(replace_str)
        temp_file.close()

        out, err, eid = system('diff -B %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        # Check that -i causes  diff to ignore the difference in case.
        out, err, eid = system('diff -B -i %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('diff -B --ignore-case %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Check -I --ignore-matching-lines=regexp
        temp_file = open(f1, 'w')
        temp_file.write(rand_str+'\n'+'1'+rand_str+'1'+'\n')
        temp_file.close()

        temp_file = open(f2, 'w')
        temp_file.write('1'+rand_str+'\n'+rand_str+'\n')
        temp_file.close()

        out, err, eid = system('diff %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 1, out+err)

        out, err, eid = system("diff -I '^[[:digit:]]' %s %s" % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system("diff --ignore-matching-lines='^[[:digit:]]' %s %s" % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Check -q --brief
        out, err, eid = system('diff -q %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn("Files /var/tmp/testf1.txt and /var/tmp/testf2.txt differ", out, out+err)

        out, err, eid = system('diff --brief %s %s' % (f1, f2))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertIn("Files /var/tmp/testf1.txt and /var/tmp/testf2.txt differ", out, out+err)

    def tearDown(self):
        system('rm %s %s' % ('/var/tmp/diffutilsa', '/var/tmp/diffutilsa'))
        system('rm %s %s' % ('/var/tmp/testf1.txt', '/var/tmp/testf2.txt'))


class TunirNonGatingtestBzip2(unittest.TestCase):

    def setUp(self):
        """Creates a file for bzip2 testing"""
        with open('/var/tmp/bzip2-test.txt', 'w') as FILE:
            FILE.write('bzip2-test of single file')

    def test_bzip2(self):
        """Test to run a file through bzip2,bzcat,bunzip2"""

        testfile = '/var/tmp/bzip2-test.txt'
        testbz2file = '/var/tmp/bzip2-test.txt.bz2'

        # Runs a file through bzip2
        out, err, eid = system('bzip2 %s' % testfile)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Runs a file through bzcat
        out, err, eid = system("bzcat %s | grep -q 'bzip2-test of single file'" % testbz2file)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Runs a file through bunzip2
        out, err, eid = system("bunzip2 %s" % testbz2file)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Checks the file contents
        out, err, eid = system("grep -q 'bzip2-test of single file' %s" % testfile)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Checks if the bz2 file exists
        self.assertFalse(os.path.exists(testbz2file))

    def tearDown(self):
        """Deletes the file created for bzip2 testing"""
        os.remove('/var/tmp/bzip2-test.txt')


class TunirNonGatingtestfile(unittest.TestCase):

    def test_file(self):
        """file test"""

        pngfile = '/usr/share/anaconda/boot/syslinux-splash.png'
        testfilepath = '/tmp/p_file_link_test'

        # Checks if file package is installed
        out, err, eid = system('rpm -q file')
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Checks if file can recognize mime executable type
        out, err, eid = system('file /bin/bash -i')
        out = out.decode('utf-8')
        self.assertIn('application/x-sharedlib', out, out)

        # Checks if file can recognize image mime file type
        out, err, eid = system('file %s -i' % pngfile)
        out = out.decode('utf-8')
        self.assertIn('image/png', out, out)

        # Checks if file can recognize symlink mime file type
        out, err, eid = system('ln -s /etc/hosts %s' % testfilepath)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        out, err, eid = system('file -i %s' % testfilepath)
        out = out.decode('utf-8')
        self.assertIn('inode/symlink', out, out)

    def tearDown(self):
        """Deletes the symlink created for test"""
        os.remove('/tmp/p_file_link_test')


class TunirNonGatingtestcurl(unittest.TestCase):

    def test_curl(self):
        """Tests that curl can access http-host and retrieve index.html"""

        URL = "http://fedoraproject.org"

        # Querying url
        out, err, eid = system('curl --location -s %s' % URL)
        out = out.decode('utf-8')
        self.assertIn('Fedora', out)


class TunirNonGatingtestaudit(unittest.TestCase):

    def test_audit(self):
        """Tests audit"""

        audit_log = '/var/log/audit/audit.log'

        # Checks if audit is installed
        out, err, eid = system('rpm -q audit')
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Checks if auditd is running
        out, err, eid = system('systemctl status auditd')
        out = out.decode('utf-8')
        self.assertIn('active', out, out)

        # Generates some events for audit log
        out, err, eid = system('useradd testauditd')
        out, err, eid = system('userdel testauditd')
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        self.assertEqual(eid, 0, out+err)

        # Checks if the right logs are in the file"
        with open(audit_log, 'r') as fobj:
            f = fobj.read()
            self.assertIn('useradd', f)
            self.assertIn('userdel', f)
            self.assertIn('testauditd', f)

if __name__ == '__main__':
    unittest.main()
