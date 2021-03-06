
#include "geodesic.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>


PYBIND11_MODULE(geodesic, m) {
    m.doc() = "Geodesic operations for spherical trigonometry";
    m.def("central_angle", &central_angle, "Compute the central angle on the sphere", 
            pybind11::arg("pt_uvec"), pybind11::arg("vert_uvec"));
    m.def("spherical2cartesian", &spherical2cartesian, "Convert spherical to cartesian", 
            pybind11::arg("spherical"));
    m.def("cartesian2spherical", &cartesian2spherical, "Convert cartesian to spherical", 
            pybind11::arg("cartesian"));

    m.def("sphere_waypoint", &sphere_waypoint, "Find waypoints between two cartesian coordinates along a great circle connecting the two",
            pybind11::arg("initial_point"), pybind11::arg("final_point"), pybind11::arg("num_points") = 5);
}

