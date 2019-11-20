// (c) Copyright 2018 by Coinkite Inc. This file is part of Coldcard <coldcardwallet.com>
// and is covered by GPLv3 license found in COPYING.
//
// Version string. Careful with changes because parsed by python code and probably others.
//
#include "version.h"

// the Makefile will define BUILD and GIT values.
const char version_string[] = RELEASE_VERSION 
#ifdef BUILD_TIME
    " time=" BUILD_TIME 
#endif
#ifdef GIT_HASH
    " git=" GIT_HASH 
#endif
#ifndef RELEASE
    " DEV=1" 
#endif
#ifndef FOR_608
    " SE=6"
#endif
;
