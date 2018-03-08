#include "input_parser.hpp"
#include "wavefront.hpp"
#include "polyhedron.hpp"

#include <Eigen/Dense>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_items_with_id_3.h>

#include <iostream>
#include <fstream>
#include <vector>

typedef CGAL::Simple_cartesian<double>     Kernel;
typedef CGAL::Polyhedron_3<Kernel, CGAL::Polyhedron_items_with_id_3>         Polyhedron;
typedef Polyhedron::HalfedgeDS             HalfedgeDS;

void eigen_to_polyhedron(Eigen::MatrixXd &V, Eigen::MatrixXi &F, Polyhedron &P) {
    Polyhedron_builder<HalfedgeDS> builder(V, F);
    P.delegate(builder);
    CGAL_assertion(P.is_triangle(P.halfedges_begin()));
}

int main(int argc, char* argv[]) {
    InputParser input(argc, argv);
    if (input.option_exists("-h")) {
        std::cout << "Usage read_obj -i input_file.obj" << std::endl;
    }
    
    // vectors of vectors to store the data
    std::vector<std::vector<double>> vector_V;
    std::vector<std::vector<int>> vector_F;
    int read_flag = 1;
    Polyhedron P;

    const std::string input_file = input.get_command_option("-i");
    if (!input_file.empty()) {
        std::cout << "Reading " << input_file << std::endl;
        /* std::ifstream input_stream(input_file); */
        /* read_flag = obj::read(input_file, vector_V, vector_F); */
        Eigen::MatrixXd V_eigen;
        Eigen::MatrixXi F_eigen;
        read_flag = obj::read_to_eigen(input_file, V_eigen, F_eigen);
        if (read_flag == 0) {
            /* Polyhedron_builder<HalfedgeDS> builder(V_eigen, F_eigen); */
            /* P.delegate(builder); */
            /* CGAL_assertion(P.is_triangle(P.halfedges_begin())); */
            eigen_to_polyhedron(V_eigen, F_eigen, P);

            std::cout << "Polyhedron is built in CGAL" << std::endl;
            std::cout << "Valid : " << P.is_valid() << std::endl;
            std::cout << "Vertices : " << P.size_of_vertices() << std::endl;
            std::cout << "Faces : " << P.size_of_facets() << std::endl;
            std::cout << "HalfEdges : " << P.size_of_halfedges() << std::endl;
        }
         
    }  // input file is closed when leaving the scope
    Eigen::MatrixXd V_poly;
    Eigen::MatrixXi F_poly;

    polyhedron_to_eigen(P, V_poly, F_poly);
    return 0;
}
