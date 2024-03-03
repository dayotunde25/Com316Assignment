<?php 
   function smallestIndex($moje, $size) {
       if ($size === 0) {
         return -1;
        }
      $index = 0;
      for ($i = 0; $i < $size; $i++) {
        if ($moje[$i] < $moje[$index]) {
           $index = $i;
        }
       }
    return $index;
   }

     $array = [10,56,79,102,16,89,312,3,8,24];
     $size = count($array);
     $index = smallestIndex($array, $size);
     if ($index === -1) {
        echo "Empty Array, No smallest number found.";
      } 
     else {
         echo "The smallest number is at index " . $index;
      }

?>
