# NYC Noise Inference

Reprodution of the work presented in:

Yu Zheng, Tong Liu, Yilun Wang, Yanmin Zhu, Yanchi Liu, and Eric Chang. 2014. Diagnosing New York city's noises with ubiquitous data. In *Proceedings of the 2014 ACM International Joint Conference on Pervasive and Ubiquitous Computing* (UbiComp '14). ACM, New York, NY, USA, 715-725. DOI=http://dx.doi.org/10.1145/2632048.2632102

- [*on hold*] Map visualization and interation 
   - Open *index.html* on a browser to see the current version.

Data collected from [NYC Open Data](https://nycopendata.socrata.com/) and [NYC Prepared](http://data.nycprepared.org).

1. Regions stabilished according to the [community districts](https://nycdatastables.s3.amazonaws.com/2013-08-19T18:22:23.125Z/community-districts-polygon.geojson) of NYC.

2. Geographical Features Considered:

 * Entertainment & Arts
    * [Museums & Galeries](https://nycdatastables.s3.amazonaws.com/2013-06-04T18:02:56.019Z/museums-and-galleries-results.csv)
 * Vehicles
    * [Parking Facilities](https://nycdatastables.s3.amazonaws.com/2013-12-16T21:49:55.716Z/nyc-parking-facilities-results.csv)
 * Business to Business
    * [NY Companies](https://nycdatastables.s3.amazonaws.com/2013-06-20T16:06:05.136Z/mapped-in-ny-companies-results.csv)
 * Education
    * [Public Schools](https://nycdatastables.s3.amazonaws.com/2013-06-11T18:59:27.269Z/nyc-public-school-locations-results.csv)
    * [Private Schools](https://nycdatastables.s3.amazonaws.com/2013-07-29T15:49:03.498Z/nyc-private-school-results.csv)
    * [Special Education](https://nycdatastables.s3.amazonaws.com/2013-07-01T16:25:00.297Z/nyc-special-education-school-results.csv)
    * [Universities & Colleges](https://nycdatastables.s3.amazonaws.com/2013-06-05T14:35:56.387Z/basic-description-of-colleges-and-universities-results.csv)
 * Food & Dining
    * [Sidewalk Cafes](https://nycdatastables.s3.amazonaws.com/2013-06-05T20:25:17.301Z/operating-sidewalk-cafes-results.csv)
 * Health & Beauty
    * [Health Centers](https://nycdatastables.s3.amazonaws.com/2013-06-04T14:40:48.764Z/community-health-centers-results.csv)
 * Profissional & Services
    * [Agencies services](https://nycdatastables.s3.amazonaws.com/2013-07-02T15:29:20.692Z/agency-service-center-results.csv)
 * Shopping
    * [Farmes Market](https://nycdatastables.s3.amazonaws.com/2013-06-13T18:39:44.536Z/nyc-2012-farmers-market-list-results.csv)
    * [Grocery Stores](https://nycdatastables.s3.amazonaws.com/2013-10-18T21:14:52.348Z/nyc-grocery-stores-final.csv)
 * Transport
    * [Subway Entrances](https://nycdatastables.s3.amazonaws.com/2013-06-18T14:29:37.626Z/subway-entrances-results.csv)
 * Travel
    * [Monuments](https://nycdatastables.s3.amazonaws.com/2013-06-04T17:58:59.335Z/map-of-monuments-results.csv)
    * [Landmarks](https://nycdatastables.s3.amazonaws.com/2013-06-18T20:17:34.010Z/nyc-landmarks-results.csv)
 * [Road bed](https://data.cityofnewyork.us/City-Government/road/svwp-sbcd)
 * [Road bed+](https://data.cityofnewyork.us/City-Government/NYC-Street-Centerline-CSCL-/exjm-f27b)
 * [Areas of Interest](https://data.cityofnewyork.us/Health/Areas-of-Interest-GIS/mzbd-kucq)
 
3. Human Mobility Features 
  * Collected using [Foursquare API](https://developer.foursquare.com/resources/libraries), specifically, the [*venus/explore*](https://developer.foursquare.com/docs/venues/explore).
  * Also, [TLC Trip Record Data](http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml).
  
4. Noise Categories
   * Obtained from the [311](http://www1.nyc.gov/311/index.page) [data](http://data.cityofnewyork.us/resource/fhrw-4uyv.json)
