//
// Copyright (C) 2017 Kevin Thornton <krthornt@uci.edu>
//
// This file is part of fwdpy11.
//
// fwdpy11 is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// fwdpy11 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with fwdpy11.  If not, see <http://www.gnu.org/licenses/>.
//
#ifndef FWDPY11_GENETIC_VALUES_MLOCUSADDITIVE_HPP__
#define FWDPY11_GENETIC_VALUES_MLOCUSADDITIVE_HPP__

#include "fwdpp_wrappers/fwdpp_mlocus_gvalue.hpp"
#include "details/pickle_additive.hpp"

namespace fwdpy11
{
    using MlocusAdditive
        = fwdpp_mlocus_gvalue<fwdpp::additive_diploid, pickle_additive>;
} // namespace fwdpy11
#endif
