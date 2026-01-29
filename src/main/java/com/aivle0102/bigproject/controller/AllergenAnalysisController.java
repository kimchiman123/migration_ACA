// ?�레르기 ?�분 분석 ?�청???�신?�는 REST 컨트롤러.
// 분석 ?�비???�출 ??결과 DTO�?반환?�다.
package com.aivle0102.bigproject.controller;

import com.aivle0102.bigproject.dto.AllergenAnalysisResponse;
import com.aivle0102.bigproject.dto.ReportRequest;
import com.aivle0102.bigproject.service.AllergenAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/allergen")
@RequiredArgsConstructor
public class AllergenAnalysisController {

    private final AllergenAnalysisService allergenAnalysisService;

    @PostMapping("/analyze")
    public ResponseEntity<AllergenAnalysisResponse> analyze(@RequestBody ReportRequest request) {
        // recipe, targetCountry�??�용 (?�머지??무시)
        AllergenAnalysisResponse resp = allergenAnalysisService.analyze(request);
        return ResponseEntity.ok(resp);
    }
}
