package com.example.cameraapp.auth;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.cameraapp.R;

import java.util.Calendar;

public class PatientDetailsActivity extends AppCompatActivity {
    String email, password,full,date;
    EditText fullname,dob;
    Button btn;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_patient_details);

        fullname = findViewById(R.id.fullName);
        dob = findViewById(R.id.dob);
        btn = findViewById(R.id.register);
        email = getIntent().getStringExtra("email");
        password = getIntent().getStringExtra("password");
        dob.setOnClickListener(v -> {

            Calendar calendar = Calendar.getInstance();

            DatePickerDialog dialog = new DatePickerDialog(
                    PatientDetailsActivity.this,
                    (view, year, month, dayOfMonth) -> {

                        String date = dayOfMonth + "/" + (month + 1) + "/" + year;
                        dob.setText(date);

                    },
                    calendar.get(Calendar.YEAR),
                    calendar.get(Calendar.MONTH),
                    calendar.get(Calendar.DAY_OF_MONTH)
            );

            dialog.show();

        });

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(fullname.getText().toString().equals("")){
                    Toast.makeText(PatientDetailsActivity.this,"Enter the name!",Toast.LENGTH_LONG).show();
                    return;
                }
                full = fullname.getText().toString();
                date= dob.getText().toString();



            }
        });


    }
}