# pylint: disable=missing-module-docstring

# Copyright 2021, joshiayus Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of joshiayus Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from tests.test_lib.test_utils.test_utils import (  # pylint: disable=unused-import
    TestCustomTypeUtilityFunction, TestWhichUtilityFunction,
    TestIgnoreWarningsUtilityFunction,
    TestRemoveFilePermissionsAndAddFilePermissionsFunction,
)
from tests.test_linkedin.test_settings import (  # pylint: disable=unused-import
    TestProtectedGetGoogleChromeBinaryVersionFunction,
    TestProtectedCheckIfChromeDriverIsCompatibleWithGoogleChromeInstalledFunction,  # pylint: disable=line-too-long
    TestProtectedGetPlatformSpecificChromeDriverCompatibleVersionUrlFunction,
)

from tests.test_linkedin.test_driver import (  # pylint: disable=unused-import
    TestProtectedDriverClass, TestProtectedMemberDriver,
    TestGChromeDriverInstanceClass, TestGetGlobalChromeDriverInstanceMethod,
    TestDisableGlobalChromeDriverInstanceMethod,
)

from tests.test_linkedin.test_login.test_login import (  # pylint: disable=unused-import
    TestLoginApiLinkedInClass,)

from tests.test_linkedin.test_message.test_template import (  # pylint: disable=unused-import
    TestFunctionReadTemplate, TestProtectedFunctionLoadMessageTemplate,
    TestProtectedFunctionCheckIfTemplateFileIsSupported,
)

from tests.test_linkedin.test_invitation.test_invitation import (  # pylint: disable=unused-import
    TestGlobalVarSuccessAndFailureRate,
    TestProtectedReplaceTemplateVarWithTemplateValue,
)

if __name__ == '__main__':
  unittest.main(verbosity=2)
