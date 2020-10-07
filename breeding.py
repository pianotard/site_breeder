class Point:
    
    def __init__(self, x, y):
        self._x = x
        self._y = y
        
    def __str__(self):
        return f'({self.x}, {self.y})'
        
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
        
    def distance(self, p):
        dx = self._x - p.x
        dy = self._y - p.y
        return (dx * dx + dy * dy) ** 0.5

class Facility:
    
    def __init__(self, name, x, y, width, height):
        self._name = name
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._min_radius = None
        self._max_radius = None
        self._min_edge_bound = None
        self._max_edge_bound = None
        
    def __str__(self):
        return f'Facility {self._name} at ({self._x}, {self._y}) with dimensions {self._width} x {self._height}'
    
    @property
    def name(self):
        return self._name
    
    @property
    def left_x(self):
        return self._x
    
    @property
    def right_x(self):
        return self._x + self._width
    
    @property
    def top_y(self):
        return self._y
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    @property
    def btm_y(self):
        return self._y + self._height
    
    @property
    def top_left(self):
        return Point(self.left_x, self.top_y)
    
    @property
    def top_right(self):
        return Point(self.right_x, self.top_y)
    
    @property
    def btm_left(self):
        return Point(self.left_x, self.btm_y)
    
    @property
    def btm_right(self):
        return Point(self.right_x, self.btm_y)
    
    @property
    def center(self):
        return Point(self.left_x + self._width / 2, self.top_y + self._height / 2)
    
    @property
    def min_radius(self):
        return self._min_radius
    
    @min_radius.setter
    def min_radius(self, radius):
        self._min_radius = radius
    
    @property
    def max_radius(self):
        return self._max_radius
    
    @max_radius.setter
    def max_radius(self, radius):
        self._max_radius = radius
        
    @property
    def min_edge_bound(self):
        return self._min_edge_bound
    
    @min_edge_bound.setter
    def min_edge_bound(self, bound):
        self._min_edge_bound = bound
        
    @property
    def max_edge_bound(self):
        return self._max_edge_bound
    
    @max_edge_bound.setter
    def max_edge_bound(self, bound):
        self._max_edge_bound = bound
    
    def contains_point(self, point):
        (x, y) = (point.x, point.y)
        return x >= self.left_x and x < self.right_x and y >= self.top_y and y < self.btm_y
    
    def overlaps(self, f):
        """
        Returns true if self overlaps with f
        """
        return self.left_x < f.right_x and self.right_x > f.left_x and \
            self.top_y < f.btm_y and self.btm_y > f.top_y
    
    def outside_min_radius(self, f):
        """
        Returns true if nearerst corner of f is outside min_radius
        """
        if self._min_radius is None:
            return True
        corners = [f.top_left, f.top_right, f.btm_left, f.btm_right]
        min_distance = min([p.distance(self.center) for p in corners])
        return min_distance >= self._min_radius
    
    def within_max_radius(self, f):
        """
        Returns true if furthest corner of f is within max_radius
        """
        if self._max_radius is None:
            return True
        corners = [f.top_left, f.top_right, f.btm_left, f.btm_right]
        max_distance = max([p.distance(self.center) for p in corners])
        return max_distance <= self._max_radius
    
    def outside_min_edge_bound(self, f):
        """
        Returns True if closest edge of f is outside min_edge_bound
        """
        if self._min_edge_bound is None:
            return True
        min_bound_box = Facility("bound", self.left_x - self.min_edge_bound, self.top_y - self.min_edge_bound,\
                                self._width + 2 * self.min_edge_bound, self._height + 2 * self.min_edge_bound)
        return not min_bound_box.overlaps(f)
    
    def within_max_edge_bound(self, f):
        """
        Returns True if closest edge of f is within max_edge_bound
        """
        if self._max_edge_bound is None:
            return True
        max_bound_box = Facility("bound", self.left_x - self.max_edge_bound, self.top_y - self.max_edge_bound,\
                                self._width + 2 * self.max_edge_bound, self._height + 2 * self.max_edge_bound)
        return max_bound_box.overlaps(f)
    
class PlacementError(Exception):
    
    def __init__(self, message, available_zones = []):
        """
        :param message: desired error message
        :param available_zones: list of tuples representing available coordinates
        """
        super().__init__(message)
        self._available_zones = available_zones
        
    @property
    def available_zones(self):
        return self._available_zones
    
class Site:
    
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._facilities = []
        self._exclusion_zones = []
        
    def __str__(self):
        facil_str = str([str(f) for f in self._facilities])
        excl_str = str([str(f.top_left) for f in self._exclusion_zones])
        picture_str = ''
        picture_str += '_' * (self._width * 2 + 1) + '\n'
        for y in range(1, self._height + 1):
            picture_str += '|'
            for x in range(1, self._width + 1):
                facility_name = self.get_facility_name(Point(x, y))
                if facility_name:
                    picture_str += facility_name
                elif self.is_exclusion_zone(Point(x, y)):
                    picture_str += 'X'
                else:
                    picture_str += ' '
                picture_str += '|'
            picture_str += '\n|'
            picture_str += '-+' * (self._width - 1)
            picture_str += '-|\n'
        return f'Site with dimensions {self._width} x {self._height}\nFacilities: {facil_str}\n' + \
        f'Exclusion zones: {excl_str}\n{picture_str}'
        
    def get_facility_name(self, point):
        """
        Gets a 1-character representation of a facility at a given point
        """
        for f in self._facilities:
            if f.contains_point(point):
                return f.name[0]
        return ''
        
    def is_exclusion_zone(self, point):
        found = [f for f in self._exclusion_zones if f.contains_point(point)]
        return found
        
    def add_exclusion_zones(self, points = []):
        """
        self.exclusion_zones is a list of 1 x 1 Facility's for now.
        May want to optimize into larger rectangles in future
        :param points: list of tuples representing x, y coordinates of exclusion zones
        """
        for point in points:
            assert self.point_within_boundaries(point), f'{point} out of boundaries'
            (x, y) = point
            self._exclusion_zones.append(Facility('ex', x, y, 1, 1))
        
    def add_facility(self, facility):
        """
        Attempts to add a facility into the Site.
        Raises a PlacementError if any of the hard constraints are broken.
        """
        if not self.facility_within_boundaries(facility): 
            self.raise_placement_error(f'Facility {facility.name} is out of bounds')
        if self.facility_overlap(facility):
            self.raise_placement_error(f'Facility {facility.name} overlaps with an existing facility')
        if self.in_exclusion_zone(facility):
            self.raise_placement_error(f'Facility {facility.name} is in an exclusion zone')
        if not self.check_radii(facility):
            self.raise_placement_error(f'Radius constraint broken when trying to add facility {facility.name}')
        if not self.check_edges(facility):
            self.raise_placement_error(f'Edge constraint broken when trying to add facility {facility.name}')
        self._facilities.append(facility)
        
    def facility_within_boundaries(self, facility):
        left = facility.left_x >= 0 and facility.left_x <= self._width + 1
        right = facility.right_x >= 0 and facility.right_x <= self._width + 1
        top = facility.top_y >= 0 and facility.top_y <= self._height + 1
        btm = facility.btm_y >= 0 and facility.btm_y <= self._height + 1
        return top and btm and left and right
    
    def point_within_boundaries(self, point):
        """
        :param point: tuple representing x, y coordinates
        """
        return point[0] >= 0 and point[0] <= self._width and point[1] >= 0 and point[1] <= self._height
    
    def facility_overlap(self, facility):
        for f in self._facilities:
            if f.overlaps(facility):
                return True
        return False
    
    def in_exclusion_zone(self, facility):
        for f in self._exclusion_zones:
            if f.overlaps(facility):
                return True
        return False
    
    def check_radii(self, facility):
        """
        Returns True if all facilities are outside of one anothers' minimum radius, OR
                        all facilities are within one anothers' maximum radius
                False otherwise
        """
        for f in self._facilities:
            if not f.outside_min_radius(facility) or not facility.outside_min_radius(f):
                return False
            if not f.within_max_radius(facility) or not facility.within_max_radius(f):
                return False
        return True
    
    def check_edges(self, facility):
        """
        Returns True if all facilities' closest edges are outside of one anothers' minimum distance, OR
                        all facilities' closest edges are within one anothers' maximum distance
                False otherwise
        """
        for f in self._facilities:
            if not f.outside_min_edge_bound(facility) or not facility.outside_min_edge_bound(f):
                return False
            if not f.within_max_edge_bound(facility) or not facility.within_max_edge_bound(f):
                return False
        return True
    
    def raise_placement_error(self, message):
        available_zones = []
        for y in range(1, self._height + 1):
            for x in range(1, self._width + 1):
                no_facility = not self.get_facility_name(Point(x, y))
                not_exclusion = not self.is_exclusion_zone(Point(x, y))
                
                dummy_facility = Facility("Dummy", x, y, 1, 1)
                radii_ok = self.check_radii(dummy_facility)
                edge_ok = self.check_edges(dummy_facility)
                
                if no_facility and not_exclusion and radii_ok and edge_ok:
                    available_zones.append((x, y))
                    
        raise PlacementError(message, available_zones)
        
class ImpossibleSiteError(Exception):
    pass

class SiteGenerator:
    
    def generate(width, height, exclusion_zones, facilities, verbose = False):
        """
        Attempts to generate a Site with all hard constraints met.
        Raises a ImpossibleSiteError otherwise.
        :param exclusion_zones: list of tuples representing exclusion zones
        :param facilities: list of Facilities representing facilities
        """
        site = Site(width, height)
        site.add_exclusion_zones(exclusion_zones)
        
        for facility in facilities:
            try:
                site.add_facility(facility)
                if verbose: print(f'Successfully added facility {facility.name}')
            except PlacementError as e:
                available_zones = e.available_zones
                if verbose: print(e)
                success = False
                while len(available_zones) > 0:
                    (x, y) = available_zones.pop(0)
                    if verbose: print(f'Attempt shift to ({x}, {y})')
                    shifted = Facility(facility.name, x, y, facility.width, facility.height)
                    try:
                        site.add_facility(shifted)
                        success = True
                        if verbose: print(f'Successfully added facility {facility.name}')
                        break
                    except:
                        continue
                if not success:
                    if verbose: print(f'Failed to add facility {facility.name}')
                    raise ImpossibleSiteError(f'Failed to add facility {facility.name}')
        
        return site
    
if __name__ == "__main__":
    f1 = Facility("1", 3, 3, 2, 1)
    f2 = Facility("2", 3, 5, 1, 2)
    f3 = Facility("3", 5, 6, 2, 1)
    f4 = Facility("4", 4, 2, 1, 1)

    facilities = [f1, f2, f3, f4]

    f1.min_radius = 1
    f1.max_radius = 3
    # f1.min_edge_bound = 1
    # f1.max_edge_bound = 2
    exclusion_zones = [(5, 6),
                       (2, 7), (3, 7), (4, 7), (5, 7)]

    (width, height) = (5, 7)

    try:
        site = SiteGenerator.generate(width, height, exclusion_zones, facilities, verbose = True)
        print(site)
    except ImpossibleSiteError as e:
        print(e)
        print(f'Site not generated')

