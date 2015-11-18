/* simple.glsl

simple diffuse lighting based on laberts cosine law; see e.g.:
    http://en.wikipedia.org/wiki/Lambertian_reflectance
    http://en.wikipedia.org/wiki/Lambert%27s_cosine_law
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec2  v_tc0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform vec4 color;

varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec4 frag_color;
varying vec2 tex_coord;

void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);
    frag_color = color;
    tex_coord = v_tc0;
    gl_Position = projection_mat * pos;

}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec4 frag_color;
varying vec2 tex_coord;
uniform sampler2D texture1;

uniform mat4 normal_mat;

void main (void){
    //correct normal, and compute light vector (assume light at the eye)
    vec4 v_normal = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );
    //reflectance based on lamberts law of cosine
    float theta = clamp(dot(v_normal, v_light), 0.8, 1.0);
    gl_FragColor = texture2D(texture1, tex_coord) * vec4(theta,theta,theta, 1.0);
}